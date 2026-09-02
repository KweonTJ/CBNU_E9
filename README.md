# CBNU 학연산 1층 로비 월드

충북대학교 학연산공동기술연구원 1층 피난안내도를 기준으로 만든 Isaac Sim 근사 월드다.

실측 복제가 아니라 현재 직각 복도 비율을 유지한 시각적 근사다. 현재 버전은 로비 바닥·문·소파·책상·ATM에 더해, 실내 천장·조명·정면 통유리 벽과 코너형 디지털 전시벽까지 포함한다.

![CBNU 학연산 1층 상세 평면도](worlds/cbnu_haksan_1f_corridor/preview_top_view_detailed.png)

## 기준 월드

```text
worlds/cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda
```

- 단위: `m`
- Up axis: `Z`
- 전체 크기: 약 `35.6 × 20.8m`
- 벽: 높이 `3.0m`, 두께 `0.20m`, 총 12개
- 천장: 실내 높이 `3.0m`, 두께 `0.10m`, 복도와 동일한 polygon
- 서쪽 긴 복도 폭: `1.73m`(기존 중심선 `y=12.2753` 유지)
- 메인 기둥: `1.2 × 1.2 × 3.0m`, 총 3개
- 모든 외곽 벽 회전: `0°` 또는 `90°`
- 기준 이미지: `worlds/cbnu_haksan_1f_corridor/reference/evacuation_diagram_annotated.png`

서쪽 긴 복도만 기존 중심선을 기준으로 폭을 `1.73m`로 줄였다. 이에 연결된 Floor/Ceiling polygon과 벽 위치를 함께 맞췄으며 기존 Floor/Wall collision은 유지했다.

## 현재 구성

| 구분 | 구성 |
| --- | --- |
| Floor | Bala White 스타일 polished granite |
| Ceiling | warm white 무광 천장, collision 유지 |
| Ceiling light | 일반 LED panel 12개, 중앙 대형 panel 1개 (`6.0 × 2.4m`) |
| Wood door | single 3개, double 4개 |
| Glass entrance | 투명 양개 유리문 2세트, 문짝 총 4개 |
| Glass wall | 투명 통유리: 정면 출입문 좌우 2장 + 북쪽 끝 1장 |
| Exterior pavement | 외부 그리드를 가리는 대형 보도블럭 광장 2개, albedo·normal texture 적용 |
| Sofa | straight 3개, corner 1개, Column 2 U형 1개 |
| Table | 하부가 채워진 목재 책상 3개 |
| Equipment | 은행 ATM 2개 |
| Architecture detail | 바닥에서 0.85m 띄운 compact L자 전시벽 1개, 긴 왼쪽 5개 + 짧은 오른쪽 3개 display |
| Entrance pillar | ATM–문 사이 1개 + 문 반대편 대칭 1개 |
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
│   ├── Ceiling
│   ├── CeilingLights
│   │   ├── CeilingLight_01 ... CeilingLight_12
│   │   └── CeilingLight_Central_Large
│   ├── FrontEntranceGlassWalls
│   │   ├── LeftFullHeightGlass
│   │   └── RightFullHeightGlass
│   ├── NorthCorridorEndGlassWall
│   └── Walls
├── Columns
│   ├── Column_01
│   ├── Column_03
│   ├── Column_02
│   ├── Entrance_Pillar_ATM_Side
│   └── Entrance_Pillar_Opposite
├── Architecture
│   └── DigitalDisplayWall_01
│       ├── MainBody
│       ├── FrontSection / right (Display_01 ... Display_03)
│       ├── SideSection / left (Display_04 ... Display_08)
│       └── Collision
├── Furniture
│   ├── Sofa_02
│   ├── Sofa_03
│   ├── Sofa_05
│   ├── Sofa_Corner_01
│   ├── Sofa_U_Column_02
│   ├── ATM_01
│   ├── ATM_02
│   ├── Table_01
│   ├── Table_02
│   └── Table_03
├── Doors
└── SpawnPoints
```

`/World/Obstacles`는 사용하지 않는다.

## 주요 시각 요소

### 실내 천장과 조명

- 천장 Material: `assets/materials/lobby/ceiling_white.usda`
- 천장 아래 면 높이: `3.0m`
- 천장 두께: `0.10m`
- 천장 XY footprint: 기존 복도 polygon과 동일
- 일반 매입형 LED panel: 12개
- 중앙 대형 조명: `6.0 × 2.4m`, 위치 `(25.0, 8.5, 2.95)`
- 일반 조명 RectLight intensity: `8000`
- 대형 조명 RectLight intensity: `12000`, normalize `false`
- DomeLight intensity: `1600`
- 천장 collision: enabled

일반 조명과 중앙 대형 조명은 asset을 분리했다. 중앙 조명의 크기와 밝기를 바꿔도 나머지 12개 조명에는 영향이 없다.

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
- Corner/U형 visible geometry는 asset별 `SofaUnified` 단일 Mesh만 사용
- Capsule/Sphere/Cube/Cylinder helper와 collision proxy는 모두 invisible
- 단일 Mesh 안의 base·seat·back topology는 서로 겹치지 않고 경계에서 맞닿으며, 직접 만든 bevel ring으로 쿠션 윤곽을 구분
- 오목한 L/U cap은 명시적으로 삼각화해 Hydra의 n-gon 분할로 면이 깨지는 문제를 방지
- Column 2 U형은 좌·하·우를 감싸고 위쪽은 열림
- U형 안쪽 면은 Column 2에 `clearance = 0`으로 접촉

Column asset과 U형 asset의 파일명 `column_2m.usda`, `sofa_u_around_2m_column.usda`는 기존 reference 호환을 위해 유지하지만, 실제 기준 폭은 `1.2m`다.

### 정면 유리 출입구

- 단일 양개문: `assets/architecture/doors/glass_door_double.usda`
- 양개문 2세트: `assets/architecture/doors/glass_door_double_pair.usda`
- 세트 수: 2
- 문짝 수: 4
- 두 세트 사이 간격: `0.44m`, 중앙 `0.44 × 2.22m` 고정 유리로 transom까지 틈 없이 채움
- 각 문짝 유리: `0.67 × 1.83m`, 하단·상단 rail 사이를 틈 없이 채움
- 문 header와 천장 사이: `4.16 × 0.72m` 고정 유리 transom과 상·하부 rail로 마감
- 유리 마감: clear architectural glass
- 유리 opacity / roughness: `0.16 / 0.08`
- 문 collision: disabled
- 문 좌우 통유리: `assets/architecture/windows/front_entrance_glass_walls.usda`
- 통유리 크기: 좌우 각 `4.85 × 2.82m`
- 통유리 opacity / roughness: `0.13 / 0.08`
- 정문 왼쪽 외벽–통유리와 양쪽 기둥–통유리 접합부는 확장 frame으로 연속 마감
- 얇은 dark metal 외곽 frame만 사용하고 중간 mullion은 두지 않음
- 출입구 좌우 기둥: `assets/structural/entrance_side_pillar.usda`
- 기둥 크기: 각각 `1.0425 × 1.0 × 3.0m`
- 기둥 뒤쪽 면은 남쪽 벽선에 두고 실내 방향으로 `1.0m` 돌출
- ATM 쪽 기둥은 ATM collision 끝 `x=20.3775`부터 문 frame 시작 `x=21.42`까지 빈 공간을 정확히 채움
- 반대쪽 기둥은 출입구 중심 `x=23.5` 기준 대칭
- 기둥 collision: disabled; 기존 남쪽 벽 collider 사용

정면 남쪽 경계의 기존 `Wall_10`은 크기와 collision을 그대로 유지한다. 불투명 벽 표현만 숨기고 유리 출입문과 양쪽 통유리 asset으로 시각을 대체했다.

### 서쪽 긴 복도와 끝 벽

- 복도 중심선: `y=12.2753`
- 복도 폭: `1.73m`
- 북쪽 경계: `y=13.1403`
- 남쪽 경계: `y=11.4103`
- 끝 벽: 불투명 `Wall_07`, 크기 `1.73 × 0.20 × 3.0m`
- 끝 벽 collision: enabled

서쪽 끝에는 유리 asset을 reference하지 않는다. 축소된 복도의 목재 문 3개는 새 벽선에 맞춘 뒤 불투명 벽에 가리지 않도록 복도 쪽으로 얕게 오프셋했으며, 문 collision은 계속 비활성화되어 있다.

### 북쪽 복도 끝 통유리

- Asset: `assets/architecture/windows/north_corridor_end_glass_wall.usda`
- 위치: 기존 `Wall_04` 자리
- 유리 크기: `3.1332 × 2.82m`
- 유리 opacity / roughness: `0.13 / 0.08`
- 유리 collision: disabled

기존 `Wall_04`는 치수 `3.3332 × 0.20 × 3.0m`와 collision을 유지한다. 불투명 표면만 숨기고 단일 통유리 패널로 시각을 대체했다.

### 외부 보도블럭 광장

- Asset: `assets/architecture/exterior/exterior_sidewalk_pavers.usda`
- Material: `assets/materials/exterior/sidewalk_pavers.usda`
- 남쪽 정문 광장: `200.0 × 100.0435m`
- 북쪽 출구 광장: `200.0 × 79.2754m`
- 표면 높이: `z=0.05m`, 하단 `z=-0.12m`인 폐쇄형 불투명 슬래브
- Material: 불투명도 `1.0`, roughness `0.88`, `2.0m` texture repeat
- Texture: 첨부 이미지 기반 회색 보도블럭 base color, tangent-space normal map과 roughness map
- Collision: disabled; 현재는 유리 밖 배경을 구성하는 시각용 geometry

두 광장은 투명 유리 너머 카메라 시야 전체를 덮도록 건물보다 훨씬 크게 확장했다. 단일 윗면 대신 옆면과 아랫면까지 닫힌 watertight slab으로 만들어 기본 지면이 경계·낮은 시야각·깊이 정밀도 문제로 드러나지 않게 했다. 첨부 이미지처럼 밝은 회색 장방형 블럭과 얇은 줄눈을 사용한다. normal map에는 줄눈 함몰과 콘크리트 미세 요철을, roughness map에는 블럭별 거칠기 편차를 넣어 조명 방향에 따라 보도블럭 질감이 드러난다.

### 코너형 디지털 전시벽

- Asset: `assets/architecture/digital_display_wall/digital_display_wall_corner.usda`
- 공용 display component: `assets/architecture/digital_display_wall/digital_display_panel.usda`
- L자 길이: 왼쪽 `4.5m`, 오른쪽 `2.5m`
- 차콜 본체 높이: `1.22m`
- 깊이: `0.30m`(기존 `0.40m`보다 벽면 돌출 축소)
- 바닥 clearance: `0.85m`(상단 높이 `2.07m`)
- display: 왼쪽 5개, 오른쪽 3개
- 모든 display 크기: `0.62 × 0.98m`(기존 세로의 `70%`)
- display 검정 bezel 폭: `0.02m`, 외곽 section trim: `0.04m`
- 배치: 북동쪽 로비/복도 분기 코너의 `Wall_02`·`Wall_03` 안쪽 면
- 위치/yaw: `(25.9724, 13.2044, 0.85)`, `0°`

흰색 header와 sign bar는 제거했다. 남은 차콜 본체는 하나의 watertight L-footprint Mesh이며, 화면 주변 검정 배경의 위·아래 여백을 줄였다. 전면·측면 body를 겹친 박스로 만들지 않아 코너의 중복 면과 z-fighting을 피했다. 각 display는 얇은 검정 4면 bezel과 bezel 전면보다 `0.009m` 들어간 저발광 screen으로 구성한다.

Collision은 render Mesh와 분리된 invisible box 2개로 L자 전체만 근사한다. 개별 screen에는 collision이 없다.

### ATM

- Asset: `assets/equipment/atm_machine.usda`
- 위치: 기존 `Sofa_04` 위치
- 구성: 본체, header, screen, keypad, card/receipt/cash slot

## 파일 구조

```text
assets/
├── architecture/
│   ├── ceiling/
│   │   ├── ceiling_panel_light.usda
│   │   └── ceiling_panel_light_large.usda
│   ├── doors/
│   │   ├── glass_door_double.usda
│   │   ├── glass_door_double_pair.usda
│   │   ├── wood_door_double.usda
│   │   └── wood_door_single.usda
│   ├── digital_display_wall/
│   │   ├── digital_display_panel.usda
│   │   └── digital_display_wall_corner.usda
│   ├── exterior/
│   │   └── exterior_sidewalk_pavers.usda
│   └── windows/
│       ├── corridor_end_glass_wall.usda
│       ├── front_entrance_glass_walls.usda
│       └── north_corridor_end_glass_wall.usda
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
│   ├── display_wall/
│   │   ├── display_screen.usda
│   │   └── display_wall_dark.usda
│   ├── furniture/brown_sofa_material.usda
│   ├── exterior/
│   │   ├── sidewalk_pavers.usda
│   │   └── textures/
│   │       ├── campus_sidewalk_pavers_basecolor.png
│   │       ├── campus_sidewalk_pavers_normal.png
│   │       └── campus_sidewalk_pavers_roughness.png
│   └── lobby/
│       ├── ceiling_white.usda
│       ├── marble_floor.usda
│       └── textures/
└── structural/
    ├── column_2m.usda
    └── entrance_side_pillar.usda

worlds/cbnu_haksan_1f_corridor/
├── cbnu_haksan_1f_corridor.usda
├── config/
│   ├── doors.json
│   ├── doors_layout.usda
│   ├── ceiling.json
│   ├── ceiling_layout.usda
│   ├── furniture.json
│   ├── furniture_layout.usda
│   ├── architecture.json
│   ├── architecture_layout.usda
│   └── geometry.json
├── reference/
│   └── evacuation_diagram_annotated.png
├── preview_top_view_detailed.png
└── preview_architecture_detail.png
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

Top view로 편집할 때 천장이 내부를 가리면 Stage에서 `/World/Environment/Ceiling`의 visibility만 임시로 끈다. 조명 위치를 함께 확인하려면 `/World/Environment/CeilingLights`는 켜 둔다.

## 수정 방법

### 천장 조명 위치·종류 수정

수정 파일:

```text
worlds/cbnu_haksan_1f_corridor/config/ceiling.json
```

일반 조명은 `type`을 생략하거나 `panel`을 사용한다. 중앙 대형 조명은 `large_panel`을 사용한다.

```json
{
  "name": "CeilingLight_Central_Large",
  "type": "large_panel",
  "position": [25.0, 8.5, 2.95],
  "yaw_deg": 0,
  "size": [6.0, 2.4]
}
```

수정 후 layout을 다시 만든다.

```bash
python3 scripts/update_cbnu_haksan_ceiling.py
```

`position`과 `yaw_deg`는 config에서 관리한다. 실제 조명 크기와 밝기는 다음 asset에서 수정한다.

```text
일반 조명: assets/architecture/ceiling/ceiling_panel_light.usda
대형 조명: assets/architecture/ceiling/ceiling_panel_light_large.usda
```

천장 본체의 높이·두께를 바꿀 때는 `geometry.json`, `ceiling.json`, 메인 world의 `Ceiling.points`를 함께 맞춰야 한다. `ceiling.json`만 바꿔도 천장 Mesh는 자동 재생성되지 않는다.

### 통유리 수정

```text
assets/architecture/windows/front_entrance_glass_walls.usda
assets/architecture/windows/north_corridor_end_glass_wall.usda
```

- 투명도: `GlassMaterial/PreviewSurface.inputs:opacity` (`0.13`)
- 표면 거칠기: `GlassMaterial/PreviewSurface.inputs:roughness` (`0.08`)
- 좌우 유리 크기: 각 `GlassPanel.xformOp:scale`
- 프레임 굵기: `OuterFrame`, `DoorSideFrame`, `TopFrame`, `BottomFrame`의 scale
- 전체 위치: 메인 world의 `/World/Environment/FrontEntranceGlassWalls.xformOp:translate`

현재 통유리는 맑은 투명 마감이다. 외부 지면은 유리를 불투명하게 만드는 대신 `/World/Environment/ExteriorSidewalkPavers`의 대형 폐쇄형 slab이 채운다. 투명 blend를 유지하려면 `opacityThreshold = 0`을 유지한다. 기존 `Wall_10`은 collision용이므로 삭제하거나 scale을 바꾸지 않는다.

서쪽 복도 끝은 통유리가 아니라 메인 world의 `/World/Environment/Walls/Wall_07` 불투명 벽이다. 폭을 바꿀 때는 `geometry.json`의 `west_corridor`, Floor/Ceiling polygon, `Wall_05`–`Wall_09`와 서쪽 복도 문 위치를 함께 맞춘다.

북쪽 복도 끝 통유리는 `/World/Environment/NorthCorridorEndGlassWall`에서 위치를 수정한다. 이 구간의 `Wall_04`도 collision용이므로 삭제하거나 scale을 바꾸지 않는다.

### 출입구 좌우 기둥 수정

```text
assets/structural/entrance_side_pillar.usda
worlds/cbnu_haksan_1f_corridor/config/geometry.json
```

기둥 폭 `1.0425m`는 ATM과 문 사이 실제 빈 폭이다. 깊이는 `1.0m`이며 뒤쪽 면은 남쪽 벽선에 맞춘다. 위치를 조정할 때는 `entrance_pillars`의 두 X 중심이 출입구 중심 `x=23.5`에서 같은 거리를 유지해야 한다.

### 메인 기둥과 통합 소파 Mesh 수정

```text
assets/structural/column_2m.usda
scripts/generate_unified_sofa_meshes.py
assets/furniture/sofa_corner.usda
assets/furniture/sofa_u_around_2m_column.usda
```

메인 기둥 단면은 `column_2m.usda`의 `Body.xformOp:scale`과 `geometry.json`의 세 `columns[].size`를 함께 맞춘다. 현재 값은 `1.2 × 1.2m`다. `Column_01`은 기존 위치에서 서쪽으로 `0.4m` 이동했으며, 세 기둥은 이후 로비 방향(`-Y`)으로 `0.30m` 함께 이동했다. `Column_03`은 계속 `Column_01`과 `Column_02`의 정확한 중점에 있다.

Column 2의 U형 소파는 기둥 외곽 `x=±0.6m`, `y=-0.6m`에 clearance 없이 접하도록 `generate_unified_sofa_meshes.py`에서 함께 재생성한다.

Corner/U형 소파의 보이는 `SofaUnified`는 생성 결과다. 윤곽·bevel·cap triangulation을 수정한 뒤 다음 명령으로 두 asset을 다시 만든다.

```bash
python3 scripts/generate_unified_sofa_meshes.py
```

위 스크립트는 render Mesh만 갱신한다. 기존 invisible collision helper와 상대경로 material reference는 유지된다.

### 디지털 전시벽 위치·외형 수정

배치 위치와 yaw는 다음 config에서 관리한다.

```text
worlds/cbnu_haksan_1f_corridor/config/architecture.json
```

```json
{
  "name": "DigitalDisplayWall_01",
  "position": [25.9724, 13.2044, 0.85],
  "yaw_deg": 0,
  "front_length": 2.5,
  "side_length": 4.5,
  "height": 1.22,
  "depth": 0.30,
  "front_display_count": 3,
  "side_display_count": 5,
  "display_width": 0.62,
  "display_height": 0.98,
  "mount_clearance": 0.85
}
```

수정 후 layout을 다시 만든다.

```bash
python3 scripts/update_cbnu_haksan_architecture.py
```

`architecture_layout.usda`는 생성 결과이므로 직접 수정하지 않는다. 현재 asset은 왼쪽 `4.5m`·오른쪽 `2.5m` footprint에 맞춰 제작되어 있으므로 길이를 실제로 바꿀 때는 config만 수정하지 말고 `digital_display_wall_corner.usda`의 L자 Mesh·frame·display 위치·collision도 함께 맞춘다. 모든 display는 공용 `digital_display_panel.usda`를 scale 없이 reference해 동일 크기를 유지한다.

재질은 다음 파일로 분리돼 있다.

```text
assets/materials/display_wall/display_wall_dark.usda
assets/materials/display_wall/display_screen.usda
```

screen은 bezel보다 앞쪽으로 나오지 않게 `screenRecessFromBezelFront = 0.009`를 유지한다.

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

복도 polygon, 벽, Floor/Ceiling point 또는 기둥 위치를 바꾸면 메인 world와 config를 함께 수정해야 한다. 서쪽 복도 폭 변경 시 인접 목재 문도 `doors.json`에서 새 벽면에 맞추고 `update_cbnu_haksan_doors.py`를 실행한다.

## 미리보기와 검증

전체 실행 순서:

```bash
cd ~/Isaac_Worlds

python3 scripts/update_cbnu_haksan_doors.py
python3 scripts/update_cbnu_haksan_furniture.py
python3 scripts/update_cbnu_haksan_ceiling.py
python3 scripts/update_cbnu_haksan_architecture.py
MPLCONFIGDIR=/tmp/cbnu_matplotlib python3 scripts/render_cbnu_haksan_preview.py
python3 scripts/validate_cbnu_haksan_detail.py
./scripts/test_world_with_isaac_usd.sh
```

검증 항목:

- 직각 벽 12개와 Column pose
- Floor/Wall collision
- 천장 footprint, 높이, 두께와 collision
- 일반 천장 조명 12개와 중앙 대형 조명 1개
- 정면 좌우 통유리 2장과 기존 `Wall_10` collider
- 폭 `1.73m`인 서쪽 복도와 불투명 `Wall_07` collider
- 북쪽 복도 끝 통유리 1장과 기존 `Wall_04` collider
- 활성 통유리·유리문의 clear glass 값과 정문 접합부 연속성
- 남쪽·북쪽 외부 보도블럭 Mesh, 불투명 material과 albedo·normal·roughness texture binding
- `1.2 × 1.2 × 3.0m` 메인 기둥 3개, 동일 X 간격과 `-Y 0.30m` 이동
- 바닥에서 `0.85m` 띄운 높이 `1.22m`의 watertight L자 전시벽, 긴 왼쪽 5개·짧은 오른쪽 3개 display
- 동일한 `0.62 × 0.98m` recessed display 8개와 `0.02m` 얇은 bezel
- 전시벽 render/collision 분리와 invisible collision helper 2개
- ATM–문 사이와 문 반대편의 동일 크기 대칭 기둥 2개
- Bala White texture, UV와 material binding
- 문 유형과 실제 leaf 수
- 소파 유형, 방향과 Column 2 접촉
- ATM 2개와 책상 asset load
- 세 책상의 filled lower body
- raw Obstacle Cube 부재
- 모든 USD reference의 상대경로와 대상 파일
- 실제 USD runtime에서 nested reference composition

현재 기준 결과:

```text
CBNU Haksan detailed lobby validation: PASS
USD references: 68 relative and resolved
CBNU Haksan composed Stage: PASS (USD 24.05)
verified composed prims: 49
preview: 2250 × 1425
architecture preview: 2250 × 1425
```

## 작업 범위 밖

- Go2 spawn
- RL policy 연결
- Reward, observation, action 수정
- Terrain 생성
- 물리 parameter tuning
- 움직이는 문과 hinge animation
- 복도 폭·polygon·기둥 위치 변경
