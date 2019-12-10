import os
from pathlib import Path
import xml.etree.ElementTree as ET
import re

drug_mask_re = re.compile(r'#{2,}')
ddi_roots = {'train': Path('data/withoutPars/DrugBank'),
                'test': Path('data/TestSetFinal/DrugBank'),
             }

for tag in ['train', 'test']:
    ddi_sentences = []
    ddi_root = ddi_roots[tag]
    for filename in os.listdir(ddi_root):
        if not filename.endswith('.xml'):
            continue

        tree = ET.parse(ddi_root / filename)
        root = tree.getroot()

        for sent in root.iter('sentence'):

            ents = []
            contains_ddi = 1

            sent_text = sent.attrib['text']

            for ent in sent.iter('entity'):
                begin_str = ent.attrib['charOffset'].split('-')[0]
                end_str = ent.attrib['charOffset'].split('-')[1]
                begin = int(begin_str.split(';')[0])
                end = int(end_str.split(';')[0])
                ents.append((begin, end))

                sent_text = sent_text[:begin] + '#' * (end - begin + 1) + sent_text[end+1:]

            masked_drug_text = drug_mask_re.sub('drug', sent_text, 0)

            if len(ents) < 2:
                continue

            for pair in sent.iter('pair'):
                if pair.attrib['ddi'].lower() != 'false':
                    contains_ddi = 2
                break

            ddi_sentences.append((contains_ddi, masked_drug_text))

    with open('ddi_dataset/{}.cat'.format(tag), 'w') as fo:
        for contains_ddi, _ in ddi_sentences:
            fo.write("{}\n".format(contains_ddi))

    with open('ddi_dataset/{}.txt.tok'.format(tag), 'w') as fo:
        for _, masked_drug_text in ddi_sentences:
            fo.write("{}\n".format(masked_drug_text))
