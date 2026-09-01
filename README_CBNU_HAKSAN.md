# CBNU 학연산 1층 로비 월드

충북대학교 학연산공동기술연구원 1층 피난안내도를 기준으로 만든 Isaac Sim 근사 월드다.

실측 복제가 아니라 현재 직각 복도 비율을 유지한 시각적 근사이며, 이번 버전은 로비 바닥·문·소파·책상·ATM 디테일에 초점을 맞췄다.

![CBNU 학연산 1층 상세 평면도](worlds/cbnu_haksan_1f_corridor/preview_top_view_detailed.png)

## 기준 월드

```text
worlds/cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda
```

- 단위: `m`
- Up axis: `Z`
- 전체 크기: 약 `35.6 × 20.8m`
- 벽: 높이 `3.0m`, 두께 `0.20m`, 총 12개
- 기둥: `2.0 × 2.0 × 3.0m`, 총 2개
- 모든 외곽 벽 회전: `0°` 또는 `90°`
- 기준 이미지: `worlds/cbnu_haksan_1f_corridor/reference/evacuation_diagram_annotated.png`

복도 polygon, 복도 폭, 기둥 위치, Floor/Wall collision은 기존 값을 유지했다.

## 현재 구성

| 구분 | 구성 |
| --- | --- |
| Floor | Bala White 스타일 polished granite |
| Wood door | single 3개, double 4개 |
| Glass entrance | 양개 유리문 2세트, 투명 문짝 총 4개 |
| Sofa | straight 3개, corner 1개, Column 2 U형 1개 |
| Table | 하부가 채워진 목재 책상 3개 |
| Equipment | 은행 ATM 1개 |
| Raw obstacle Cube | 없음 |

### 책상 크기

| 이름 | 크기 | 용도 |
| --- | --- | --- |
| `Table_01` | `2.8406 × 1.36m` | `Sofa_03` 앞 |
| `Table_02` | `3.2174 × 1.36m` | `Sofa_05` 앞 |
| `Table_03` | `1.6232 × 0.82m` | 서쪽 두 문 사이의 기존 `Sofa_01` 대체 |

세 책상 모두 `lobby_table_filled.usda`를 사용하며 상판 아래가 바닥부터 apron까지 채워져 있다.

## Stage 구조

```text
/World
├── PhysicsScene
├── DomeLight
├── Looks
├── Environment
│   ├── Floor
│   └── Walls
├── Columns
│   ├── Column_01
│   └── Column_02
├── Furniture
│   ├── Sofa_02
│   ├── Sofa_03
│   ├── Sofa_05
│   ├── Sofa_Corner_01
│   ├── Sofa_U_Column_02
│   ├── ATM_01
│   ├── Table_01
│   ├── Table_02
│   └── Table_03
├── Doors
└── SpawnPoints
```

`/World/Obstacles`는 사용하지 않는다.

## 주요 시각 요소

### 화강암 바닥

- Material: `assets/materials/lobby/marble_floor.usda`
- Texture: `assets/materials/lobby/textures/bala_white_granite_floor_pattern.png`
- 반복 크기: 약 `2.4m`
- Roughness: `0.24`
- Clearcoat: `0.26`
- 기존 Floor point, face topology와 collision은 유지

파일명은 기존 호환성을 위해 `marble_floor.usda`를 유지하지만 현재 표현은 대리석이 아니라 Bala White 계열 화강암이다.

### 소파

- 공통 재질: `assets/materials/furniture/brown_sofa_material.usda`
- 색상: 브라운 계열 soft matte upholstery
- 팔걸이 없음
- 일반 소파는 벽에 붙고 좌석은 로비를 향함
- Corner/U형 seat와 back은 각각 하나의 `catmullClark` 통합 Mesh
- Column 2 U형은 좌·하·우를 감싸고 위쪽은 열림
- U형 안쪽 면은 Column 2에 `clearance = 0`으로 접촉

### 정면 유리 출입구

- 단일 양개문: `assets/architecture/doors/glass_door_double.usda`
- 양개문 2세트: `assets/architecture/doors/glass_door_double_pair.usda`
- 세트 수: 2
- 문짝 수: 4
- 두 세트 사이 간격: `0.44m`
- 유리 opacity: `0.16`
- 문 collision: disabled

### ATM

- Asset: `assets/equipment/atm_machine.usda`
- 위치: 기존 `Sofa_04` 위치
- 구성: 본체, header, screen, keypad, card/receipt/cash slot

## 파일 구조

```text
assets/
├── architecture/doors/
│   ├── glass_door_double.usda
│   ├── glass_door_double_pair.usda
│   ├── wood_door_double.usda
│   └── wood_door_single.usda
├── equipment/
│   └── atm_machine.usda
├── furniture/
│   ├── lobby_table.usda
│   ├── lobby_table_filled.usda
│   ├── sofa_corner.usda
│   ├── sofa_single.usda
│   ├── sofa_straight.usda
│   └── sofa_u_around_2m_column.usda
├── materials/
│   ├── furniture/brown_sofa_material.usda
│   └── lobby/
│       ├── marble_floor.usda
│       └── textures/
└── structural/
    └── column_2m.usda

worlds/cbnu_haksan_1f_corridor/
├── cbnu_haksan_1f_corridor.usda
├── config/
│   ├── doors.json
│   ├── doors_layout.usda
│   ├── furniture.json
│   ├── furniture_layout.usda
│   └── geometry.json
├── reference/
│   └── evacuation_diagram_annotated.png
└── preview_top_view_detailed.png
```

## Isaac Sim에서 열기

```bash
cd ~/Isaac_Worlds
```

Isaac Sim GUI에서 다음 파일을 연다.

```text
~/Isaac_Worlds/worlds/cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda
```

`assets/`와 `worlds/`의 상대 위치를 유지해야 한다. USD reference에는 `/home/a/...` 같은 절대경로를 넣지 않는다.

설정이나 asset을 수정한 뒤 GUI에 변화가 없으면 기존 Stage를 닫고 같은 파일을 다시 연다. 하위 reference layer는 열린 Stage에서 이전 값이 남을 수 있다.

## 수정 방법

### 가구 위치·크기 수정

수정 파일:

```text
worlds/cbnu_haksan_1f_corridor/config/furniture.json
```

주요 필드:

| 필드 | 의미 |
| --- | --- |
| `type` | `straight`, `corner`, `u_column`, `atm`, `lobby_table_filled` |
| `position` | `[x, y, z]`, 단위 `m` |
| `yaw_deg` | Z축 회전각 |
| `length_scale` | 책상·직선 소파의 가로 scale |
| `depth_scale` | 책상의 세로 scale, 생략 시 `1.0` |
| `placement` | `wall_attached`, `column_attached`, `freestanding` |
| `facing` | `lobby`, `outward`, `not_applicable` |

책상 기본 크기는 `2.0 × 1.36m`다.

```text
실제 가로 = 2.0 × length_scale
실제 세로 = 1.36 × depth_scale
```

예시:

```json
{
  "name": "Table_03",
  "type": "lobby_table_filled",
  "position": [16.4245, 6.3188, 0.0],
  "yaw_deg": 90,
  "length_scale": 0.8116,
  "depth_scale": 0.602941,
  "placement": "wall_attached",
  "facing": "not_applicable"
}
```

수정 후 layout을 다시 만든다.

```bash
python3 scripts/update_cbnu_haksan_furniture.py
```

`furniture_layout.usda`는 생성 결과이므로 위치를 바꿀 때 직접 수정하지 않는다.

### 문 위치·종류 수정

수정 파일:

```text
worlds/cbnu_haksan_1f_corridor/config/doors.json
```

지원 유형:

| type | 의미 |
| --- | --- |
| `single` | 목재 single door |
| `double` | 목재 double door |
| `double_glass_pair` | 간격이 있는 양개 유리문 2세트 |

예시:

```json
{
  "name": "Door_Double_05",
  "type": "double_glass_pair",
  "position": [23.5, 0.17, 0.0],
  "yaw_deg": 0
}
```

수정 후 layout을 다시 만든다.

```bash
python3 scripts/update_cbnu_haksan_doors.py
```

유리문 두 세트의 간격을 바꾸려면 `glass_door_double_pair.usda`의 다음 값을 함께 수정한다.

```text
cbnu:gapBetweenSets
DoubleDoorSet_01 xformOp:translate
DoubleDoorSet_02 xformOp:translate
```

좌우 translate는 같은 절댓값과 반대 부호를 사용한다.

### 바닥 무늬 수정

현재 texture를 같은 파일명으로 교체하거나 `marble_floor.usda`의 `GraniteAlbedo.inputs:file`을 상대경로로 변경한다.

```text
assets/materials/lobby/textures/bala_white_granite_floor_pattern.png
```

광택은 `roughness`, `clearcoat`, `clearcoatRoughness`로 조절한다. 거울처럼 보이지 않도록 roughness를 지나치게 낮추지 않는다.

### 소파 색상 수정

```text
assets/materials/furniture/brown_sofa_material.usda
```

네 소파 asset이 이 material을 공유한다. 색상이나 roughness를 한 번 수정하면 모든 소파에 같이 적용된다.

### 복도·기둥 수정 시 주의

`geometry.json`은 현재 구조의 기준값을 기록한 config다. 이 파일을 수정한다고 메인 world geometry가 자동 재생성되지는 않는다.

복도 polygon, 벽, Floor point 또는 기둥 위치를 바꾸려면 별도 geometry 재생성 작업이 필요하다. 시각 디테일만 수정할 때는 건드리지 않는다.

## 미리보기와 검증

전체 실행 순서:

```bash
cd ~/Isaac_Worlds

python3 scripts/update_cbnu_haksan_doors.py
python3 scripts/update_cbnu_haksan_furniture.py
MPLCONFIGDIR=/tmp/cbnu_matplotlib python3 scripts/render_cbnu_haksan_preview.py
python3 scripts/validate_cbnu_haksan_detail.py
./scripts/test_world_with_isaac_usd.sh
```

검증 항목:

- 직각 벽 12개와 Column pose
- Floor/Wall collision
- Bala White texture, UV와 material binding
- 문 유형과 실제 leaf 수
- 소파 유형, 방향과 Column 2 접촉
- ATM과 책상 asset load
- 세 책상의 filled lower body
- raw Obstacle Cube 부재
- 모든 USD reference의 상대경로와 대상 파일
- 실제 USD runtime에서 nested reference composition

현재 기준 결과:

```text
CBNU Haksan detailed lobby validation: PASS
USD references: 30 relative and resolved
CBNU Haksan composed Stage: PASS (USD 24.05)
preview: 2250 × 1425
```

## 작업 범위 밖

- Go2 spawn
- RL policy 연결
- Reward, observation, action 수정
- Terrain 생성
- 물리 parameter tuning
- 움직이는 문과 hinge animation
- 복도 폭·polygon·기둥 위치 변경
