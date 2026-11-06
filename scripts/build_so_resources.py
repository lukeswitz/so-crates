#!/usr/bin/env python3
import gzip
import json
import os
import sys

import yaml

YamlLoader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)


def _slim(entry):
    return {
        'name': entry.get('name', ''),
        'description': entry.get('description', ''),
        'questions': [
            {'question': q.get('question', ''), 'context': q.get('context', '')}
            for q in (entry.get('questions') or [])
        ],
    }


def _write_index(index, out_dir, detection_type):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{detection_type}.json.gz')
    with gzip.open(out_path + '.tmp', 'wt', encoding='utf-8') as f:
        json.dump(index, f)
    os.replace(out_path + '.tmp', out_path)
    print(f'{len(index)} {detection_type} entries -> {out_path}')


def build_playbooks(src_repo, out_dir):
    src = os.path.join(src_repo, 'public')
    for detection_type, engine_file in (('nids', 'engine_nids.yaml'), ('sigma', 'engine_sigma.yaml')):
        index = {}
        individual_dir = os.path.join(src, detection_type, 'individual')
        for filename in os.listdir(individual_dir):
            if filename.endswith('.yaml'):
                with open(os.path.join(individual_dir, filename)) as f:
                    index[filename[:-len('.yaml')]] = _slim(yaml.load(f, Loader=YamlLoader))
        with open(os.path.join(src, detection_type, 'engine', engine_file)) as f:
            index['_default'] = _slim(yaml.load(f, Loader=YamlLoader))
        _write_index(index, out_dir, detection_type)


def build_ai_summaries(src_repo, out_dir):
    src = os.path.join(src_repo, 'detections-ai')
    for detection_type, filename in (('nids', 'suricata_summaries.yaml'),
                                     ('sigma', 'sigma_summaries.yaml'),
                                     ('yara', 'yara_summaries.yaml')):
        with open(os.path.join(src, filename)) as f:
            data = yaml.load(f, Loader=YamlLoader)
        index = {rule_id: entry.get('Summary', '').strip() for rule_id, entry in data.items()
                 if entry.get('Reviewed') and (entry.get('Summary') or '').strip()}
        _write_index(index, out_dir, detection_type)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit('Usage: build_so_resources.py <playbooks repo> <summaries repo> <playbooks out> <summaries out>')
    build_playbooks(sys.argv[1], sys.argv[3])
    build_ai_summaries(sys.argv[2], sys.argv[4])
