#!/usr/bin/env python3
"""Compile the original browser campaign into deterministic ca65 SNES tables.

Source: ../data.json, an unmodified JSON serialization of campaign-data.mjs.
No dependencies other than Python 3.10+. Run from any working directory.
The generator validates IDs, progression, and byte limits before writing output.

Room door layout is an adaptation for SNES, preserving the original room graph.
Nothing in this script claims 4-6 hours of measured play time.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parent.parent
KINDS = ['sword', 'armor', 'accessory', 'relic', 'spell', 'consumable', 'key']
NONE = 255


def ascii_name(value: str) -> str:
    value = value.replace('·', '-').replace('—', '-').replace('–', '-')
    return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().upper()[:28]


def closure(data: dict, allow_optional: bool = True, forbid: set[str] | None = None):
    """Monotone graph reachability, assuming encountered boss fights can be won.

    No boss reward is available before that boss is explicitly defeated.
    Clearing a boss is distinct from merely entering its room. The room's item
    list repeats rewards in the web source, so these are excluded from pickups.
    This validates route/gate logic, not combat balance or physical reachability.
    """
    forbid = forbid or set()
    rooms = {r['id']: r for r in data['rooms']}
    bosses = {b['room']: b for b in data['bosses']}
    item_defs = {i['id']: i for i in data['items']}
    owned = set(data['rules']['startingItems'])
    reached = {'C01'}
    defeated = set()
    stages = []
    changed = True
    while changed:
        changed = False
        stage = {'rooms': [], 'bosses': [], 'items': []}
        # Each wave is frozen so progress ordering is deterministic and inspectable.
        before_rooms, before_items = set(reached), set(owned)
        for rid in sorted(before_rooms):
            room = rooms[rid]
            boss = bosses.get(rid)
            if boss and boss['id'] not in defeated and boss['id'] not in forbid:
                if allow_optional or not boss['optional']:
                    defeated.add(boss['id'])
                    stage['bosses'].append(boss['id'])
                    owned.update(boss['rewards'])
                    changed = True
            for iid in room['items']:
                if item_defs[iid]['acquisition'] != 'boss':
                    owned.add(iid)
            # Engine must bar exits during an active boss fight. A permanently
            # forbidden boss here is treated as an impassable combat encounter.
            if boss and boss['id'] not in defeated:
                continue
            for edge in room['exits']:
                dest = rooms[edge['to']]
                if not allow_optional and (edge['secret'] or dest['type'] in {'optional', 'secret', 'secret_boss'}):
                    continue
                if set(edge['requires']) <= before_items and edge['to'] not in reached:
                    reached.add(edge['to'])
                    stage['rooms'].append(edge['to'])
                    changed = True
        stage['items'] = sorted(owned - before_items)
        if stage['items']:
            changed = True
        if any(stage.values()):
            stages.append(stage)
    return reached, owned, defeated, stages


def validate(data: dict) -> dict:
    rooms, items, regions, bosses = (data[k] for k in ('rooms', 'items', 'regions', 'bosses'))
    assert [len(rooms), len(items), len(regions), len(bosses)] == [60, 60, 8, 10]
    for group in (rooms, items, regions, bosses):
        assert len({x['id'] for x in group}) == len(group), 'Duplicate ID'
    room_ids = {x['id'] for x in rooms}
    item_ids = {x['id'] for x in items}
    region_ids = {x['id'] for x in regions}
    for room in rooms:
        assert room['region'] in region_ids
        assert len(room['exits']) <= 4 and len(room['items']) <= 3
        assert set(room['items']) <= item_ids
        for edge in room['exits']:
            assert edge['to'] in room_ids
            assert len(edge['requires']) <= 4
            assert set(edge['requires']) <= item_ids
    for boss in bosses:
        assert boss['room'] in room_ids
        assert set(boss['rewards']) <= item_ids
        assert len(boss['rewards']) <= 3
        assert set(boss['rewards']) <= set(next(r for r in rooms if r['id'] == boss['room'])['items'])
    reached, owned, defeated, stages = closure(data)
    assert reached == room_ids, f'Unreachable rooms: {room_ids - reached}'
    assert owned == item_ids, f'Unobtainable items: {item_ids - owned}'
    assert len(defeated) == 10
    main_rooms, main_items, main_bosses, _ = closure(data, allow_optional=False)
    assert 'boss_regent' in main_bosses, 'Main ending blocked by optional content'
    assert 'sword_tempest' not in main_items, 'Ultimate sword should require secret quest'
    assert 'sword_tempest' not in data['rules']['startingItems']
    assert 'H07' in main_rooms
    # Removing any mandatory progression boss must prevent reaching the ending.
    critical = {}
    for boss in bosses[:7]:
        _, _, defeats_without, _ = closure(data, forbid={boss['id']})
        critical[boss['id']] = 'boss_regent' not in defeats_without
        assert critical[boss['id']], f'Mandatory progression bypass: {boss["id"]}'
    return {
        'status': 'passed', 'source': 'original campaign-data.mjs serialized without edits',
        'rooms': len(rooms), 'regions': len(regions), 'items': len(items), 'bosses': len(bosses),
        'max_exits': max(len(r['exits']) for r in rooms),
        'max_exit_requirements': max(len(e['requires']) for r in rooms for e in r['exits']),
        'max_room_items': max(len(r['items']) for r in rooms),
        'all_rooms_reachable': len(reached), 'all_items_obtainable': len(owned),
        'all_bosses_reachable': len(defeated), 'main_route_without_secrets_completable': True,
        'main_route_room_count': len(main_rooms), 'mandatory_bosses_cannot_be_bypassed': critical,
        'progression_waves': stages,
        'limits': 'Graph logic only. Assumes every reached boss can be defeated and reachable pickups can be collected. Does not verify combat balance, physical geometry, emulator behavior, or campaign duration.'
    }


def compile_content(data: dict, tables: dict | None = None) -> str:
    if tables is None:
        tables = {}
    rooms, items, regions, bosses = (data[k] for k in ('rooms', 'items', 'regions', 'bosses'))
    room_id = {v['id']: i for i, v in enumerate(rooms)}
    item_id = {v['id']: i for i, v in enumerate(items)}
    region_id = {v['id']: i for i, v in enumerate(regions)}
    boss_id = {v['id']: i for i, v in enumerate(bosses)}
    boss_by_room = {v['room']: boss_id[v['id']] for v in bosses}
    effects = list(dict.fromkeys(i['ability'] for i in items))
    effect_id = {v: i for i, v in enumerate(effects)}
    lines = ['; GENERATED by tools/build_content.py. Do not edit by hand.',
             '; Original IDs and room graph preserved. All numeric arrays contain unsigned bytes.',
             '; Place this include within the bank-1 DATA segment selected by the engine.',
             'ROOM_COUNT = 60', 'REGION_COUNT = 8', 'ITEM_COUNT = 60', 'BOSS_COUNT = 10',
             'ROOM_EXIT_STRIDE = 4', 'ROOM_REQ_STRIDE = 4', 'ROOM_ITEM_STRIDE = 3',
             'NAME_STRIDE = 32', 'ID_NONE = 255', 'ROOM_FLAG_CHECKPOINT = 1',
             'ROOM_FLAG_BOSS = 2', 'ROOM_FLAG_SECRET = 4',
             'ROOM_FLAG_OPTIONAL = 8', 'ROOM_FLAG_BOSS_SAVE = 16',
             'FLOOR_Y = 184', 'PLAYER_START_X = 112', 'PLAYER_START_Y = 168', '']
    for prefix, ids in [('ROOM', room_id), ('ITEM', item_id), ('REGION', region_id), ('BOSS', boss_id), ('EFFECT', effect_id)]:
        for name, value in ids.items():
            lines.append(f'{prefix}_{name.upper()} = {value}')
        lines.append('')
    for n, k in enumerate(KINDS):
        lines.append(f'KIND_{k.upper()} = {n}')
    lines.append('')

    def arr(label, seq, cols=16):
        seq = list(seq)
        tables[label] = seq
        assert all(isinstance(n, int) and 0 <= n < 256 for n in seq), (label, seq)
        lines.append(label + ':')
        for start in range(0, len(seq), cols):
            lines.append('  .byte ' + ','.join(str(n) for n in seq[start:start + cols]))
        lines.append('')

    def names(label, values):
        tables[label] = [ascii_name(value) for value in values]
        lines.append(label + '_ptr:')
        for start in range(0, len(values), 8):
            lines.append('  .word ' + ','.join(f'.loword({label}_{i})' for i in range(start, min(start + 8, len(values)))))
        lines.append(label + ':')
        for i, value in enumerate(values):
            encoded = ascii_name(value).encode('ascii')
            assert len(encoded) <= 28
            lines.append(f'{label}_{i}:')
            lines.append('  .byte ' + ','.join(map(str, encoded + bytes(32 - len(encoded)))))
        lines.append('')

    arr('door_x', [24, 88, 152, 216])
    arr('pickup_x', [64, 128, 192])
    arr('starting_items', [item_id[i] for i in data['rules']['startingItems']] + [NONE])
    arr('starting_owned', [int(i['id'] in data['rules']['startingItems']) for i in items])
    arr('starting_counts', [data['rules'].get('startingConsumableCounts', {}).get(i['id'], int(i['id'] in data['rules']['startingItems'])) for i in items])
    arr('room_region', [region_id[r['region']] for r in rooms])
    arr('room_type', [(1 if r['checkpoint'] else 0) | (2 if r['id'] in boss_by_room else 0) | (4 if r['type'].startswith('secret') else 0) | (8 if r['type'] == 'optional' else 0) | (16 if r.get('bossEntranceSave') else 0) for r in rooms])
    arr('room_boss', [boss_by_room.get(r['id'], NONE) for r in rooms])
    arr('room_exit_count', [len(r['exits']) for r in rooms])
    padded_edges = [r['exits'] + [None] * (4 - len(r['exits'])) for r in rooms]
    arr('room_exit_to', [room_id[e['to']] if e else NONE for edges in padded_edges for e in edges], 4)
    arr('room_exit_secret', [int(bool(e and e['secret'])) for edges in padded_edges for e in edges], 4)
    arr('room_exit_flags', [(int(e['secret']) | (int(e['shortcut']) << 1) | (int(e['oneWay']) << 2)) if e else 0 for edges in padded_edges for e in edges], 4)
    requirements = [[item_id[i] for i in e['requires']] + [NONE] * (4 - len(e['requires'])) if e else [NONE] * 4 for edges in padded_edges for e in edges]
    # Separate component tables allow simple 16-bit X indexing without multiply.
    for n in range(4):
        arr(f'room_exit_req{n}', [req[n] for req in requirements], 4)
    arr('room_item_count', [len(r['items']) for r in rooms])
    arr('room_items', [v for r in rooms for v in ([item_id[i] for i in r['items']] + [NONE] * (3 - len(r['items'])))], 3)
    # y denotes the upper collision surface in pixels. The floor is always 184.
    # All routes remain floor-accessible; these ledges add jump combat routes.
    layouts = [
        [(40, 152, 48), (144, 120, 56)],
        [(24, 120, 48), (120, 152, 56)],
        [(40, 144, 56), (160, 144, 56)],
        [(16, 152, 56), (104, 120, 48), (184, 152, 56)],
    ]
    platforms = [[] if r['checkpoint'] else ([(40, 136, 48), (168, 136, 48)] if r['id'] in boss_by_room else layouts[i % len(layouts)]) for i, r in enumerate(rooms)]
    arr('room_platform_count', [len(p) for p in platforms])
    for label, offset, default in [('x', 0, 0), ('y', 1, NONE), ('w', 2, 0)]:
        arr('room_platform_' + label, [v[offset] for p in platforms for v in p + [(0, NONE, 0)] * (3 - len(p))], 3)
    arr('room_enemy_count', [0 if r['checkpoint'] or r['id'] in boss_by_room else 2 + (i % 2) for i, r in enumerate(rooms)])
    arr('room_enemy_kind', [(region_id[r['region']] + i) % 4 for i, r in enumerate(rooms)])
    arr('region_enemy_hp', [22, 30, 36, 45, 55, 64, 74, 88])
    arr('region_enemy_damage', [5, 7, 8, 10, 12, 14, 16, 18])
    arr('item_kind', [KINDS.index(i['kind']) for i in items])
    arr('item_power', [i.get('power', 0) for i in items])
    arr('item_effect', [effect_id[i['ability']] for i in items])
    arr('item_room', [room_id.get(i.get('room'), NONE) for i in items])
    arr('item_flags', [(int(i.get('permanent', False)) | (int(i.get('ultimate', False)) << 1) | (int(i.get('acquisition') == 'boss') << 2) | (int(i.get('stackable', False)) << 3)) for i in items])
    arr('item_mana_cost', [i.get('manaCost', 0) for i in items])
    arr('item_max_stack', [i.get('maxStack', 1) for i in items])
    arr('sword_power', [i['power'] for i in items[:12]])
    arr('sword_attack_frames', [max(5, round(24 / i['attackSpeed'])) for i in items[:12]])
    arr('sword_reach', [round(26 * i['reach']) for i in items[:12]])
    arr('sword_effect', [effect_id[i['ability']] for i in items[:12]])
    lines.append('; Q8.8 speed multiplier preserves 2.8x supreme sword without byte clipping.')
    tables['sword_speed_q8'] = [round(256 * i['attackSpeed']) for i in items[:12]]
    lines.append('sword_speed_q8:')
    lines.append('  .word ' + ','.join(str(round(256 * i['attackSpeed'])) for i in items[:12]))
    lines.append('')
    arr('boss_room', [room_id[b['room']] for b in bosses])
    arr('boss_region', [region_id[b['region']] for b in bosses])
    arr('boss_optional', [int(b['optional']) for b in bosses])
    arr('boss_rewards', [v for b in bosses for v in [item_id[i] for i in b['rewards']] + [NONE] * (3 - len(b['rewards']))], 3)
    tables['boss_hp'] = [420,620,780,1000,1250,1450,1650,2200,1500,1800]
    lines.append('boss_hp:')
    lines.append('  .word 420,620,780,1000,1250,1450,1650,2200,1500,1800')
    lines.append('')
    arr('boss_damage', [8, 10, 12, 14, 16, 18, 20, 24, 20, 22])
    arr('boss_pattern', list(range(10)))
    arr('region_start_room', [room_id[r['startRoom']] for r in regions])
    names('room_name', [r['name'] for r in rooms])
    names('region_name', [r['name'] for r in regions])
    names('item_name', [i['name'] for i in items])
    names('boss_name', [b['name'] for b in bosses])
    tables['constants'] = {line.split(' = ')[0]: int(line.split(' = ')[1]) for line in lines if ' = ' in line and line.split(' = ')[1].isdigit()}
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=ROOT / 'assets/data.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'assets/data.inc')
    parser.add_argument('--tables', type=Path, default=ROOT / 'assets/tables.json')
    parser.add_argument('--report', type=Path, default=ROOT / 'assets/validation.json')
    args = parser.parse_args()
    source = args.input.read_bytes()
    data = json.loads(source)
    report = validate(data)
    tables = {}
    output = compile_content(data, tables)
    args.tables.parent.mkdir(parents=True, exist_ok=True)
    args.tables.write_text(json.dumps(tables, ensure_ascii=False, indent=2) + '\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding='ascii')
    report['source_sha256'] = hashlib.sha256(source).hexdigest()
    report['assembler_sha256'] = hashlib.sha256(output.encode('ascii')).hexdigest()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in {'progression_waves', 'mandatory_bosses_cannot_be_bypassed'}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
