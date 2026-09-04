# CBNU 학연산 1층 로비 Isaac Sim 월드

충북대학교 학연산공동기술연구원 1층 피난안내도를 바탕으로 제작한 Isaac Sim용 실내 로비 월드다.

실측 CAD 복제가 아니라 안내도와 현장 이미지를 기준으로 비율과 동선을 근사한 환경이다. 현재 버전은 로비·복도 구조, 가구, 출입문, 전시 구조물, 엘리베이터 철문, 이동식 안내판, 실내 조명과 물리 반응형 택배 박스를 포함한다.

![CBNU 학연산 1층 상세 평면도](worlds/cbnu_haksan_1f_corridor/preview_top_view_detailed.png)

## 빠른 시작

기준 Stage:

<code>worlds/cbnu_haksan_1f_corridor/cbnu_haksan_1f_corridor.usda</code>

Isaac Sim GUI에서 위 파일을 연다. 프로젝트 내부 USD는 상대경로 reference를 사용하므로 <code>assets/</code>와 <code>worlds/</code>의 상대 위치를 유지해야 한다.

~~~bash
cd /home/a/Isaac_Worlds
./scripts/test_world_with_isaac_usd.sh
~~~

수정한 하위 layer가 GUI에 바로 반영되지 않으면 열린 Stage를 닫고 기준 Stage를 다시 연다.

## 현재 월드 요약

| 구분 | 현재 구성 |
| --- | --- |
| 기준 단위 | meter, Z-up |
| 전체 범위 | 약 35.6 × 20.8m |
| 외곽 구조 | 높이 3.0m, 두께 0.20m의 직각 벽 12개 + 정면 낮은 외벽 2개, 안쪽 코너 4곳 연속 접합 |
| 바닥 | Bala White 계열 polished granite |
| 천장 | 높이 3.0m, 두께 0.10m의 흰색 무광 천장 |
| 조명 | 일반 LED 패널 15개 + 중앙 6.0 × 2.4m 대형 패널 1개 |
| 냉방 | 중앙 대형 조명 좌우에 1.1 × 1.1m 4방향 천장 카세트 에어컨 2대 |
| 기둥 | 1.2 × 1.2 × 3.0m 메인 기둥 3개 + 정문 측면 기둥 2개 |
| 문 | 목재 single 4개, 목재 double 2개, 동쪽 흰색 양개문+목재 포털 2개, 정문 양개 유리문 2세트 |
| 가구 | 갈색 직선 소파 3개 + 검정·회색빛이 강한 어두운 적갈색 가죽 코너/U형 소파 2개, 하부가 채워진 책상 3개, ATM 2개 |
| 전시 구조 | `학연산공통기술연구원` 벽면 글자가 있는 L자 전시벽 1개(왼쪽 6개·오른쪽 3개 화면), 유리창 연결용 나무 가벽 1개, Column 03 대형 화면 1개, 회색 포스터 2개 |
| 엘리베이터 | Wall 05 스테인리스 중앙개폐식 철문 2개 |
| 북측 단상 | 1.02m 하부벽과 상부 유리 앞 3.1332 × 0.60 × 0.15m 목재 단상 1개 + 초록색 바퀴형 안내판 3개 |
| 동적 장애물 | Table 03 앞 9개 + 정문 안쪽 4개 + 엘리베이터 사이 3개, 총 16개 택배 박스 |
| 하늘 | DomeLight 기본 흰색 배경, intensity 1600 |

## 공간별 구성

### 메인 로비

- `Wall_02–03`, `Wall_05–06`, `Wall_08–09`, `Wall_11–12`의 안쪽 코너는 수평 벽 끝을 인접 세로 벽의 실내면까지 `0.10m` 연장했다. 벽 높이 전체와 collision이 끊기지 않으며 코너 외곽선에는 돌출 단차가 없다.
- 메인 기둥은 <code>Column_01</code>, <code>Column_03</code>, <code>Column_02</code> 순으로 배치된다.
- <code>Column_03</code>은 바깥쪽 두 기둥의 정확한 중점에 있으며 정문 방향 면에 1.0 × 1.45m 화면 1장이 달려 있다.
- L자 전시벽의 스크린 6개 면 상단에는 검정색 `학연산공통기술연구원` 돌출 Mesh 글자가 3.6 × 0.38 × 0.016m 크기로 벽에 직접 부착되어 있다. 투명 텍스처를 사용하지 않아 GUI 렌더 모드와 무관하게 형상이 표시된다.
- L자 전시벽은 3개 화면 쪽 길이 2.50m를 유지하고 반대쪽을 6.288533m로 확장해 화면을 5개에서 6개로 늘렸다. 6개 화면은 0.24m 간격을 유지하며 회색 면 양 끝 여백은 각각 동일한 0.5342665m다. 화면 바로 둘레의 회색 frame 여백도 양 끝 각각 0.10m다.
- 6개 화면 쪽 회색 본체 끝과 북측 유리창 오른쪽 프레임 사이에는 `WoodPartition_01`이 이어진다. 가벽 길이는 기존 2.0656m의 2/3인 1.377067m로 줄었으며, 두께 0.30m와 높이 3.00m는 유지한다. 줄어든 0.688533m만큼 디스플레이 본체가 늘어나 두 구조 사이에 틈이 없다.
- <code>Column_02</code>는 검정·회색빛이 강하고 적갈색 언더톤이 남은 가죽의 상단이 열린 U형 소파가 둘러싸며 소파 안쪽 면과 기둥 사이 clearance는 0이다.
- 남동쪽 코너의 <code>Sofa_Corner_01</code>도 같은 어두운 차콜 적갈색 가죽 재질을 사용한다.
- 로비 동쪽과 남쪽에는 벽 부착 소파·책상과 ATM이 배치돼 있다.
- 정문 오른쪽 <code>Wall_11</code>에는 <code>Door_Single_04</code>와 밝은 회색 <code>GrayPoster_01</code>이 있다.
- 동쪽 끝 `Wall_01`의 `Door_Double_03`, `Door_Double_04`는 불투명한 웜화이트 양개문이다. 각 문은 좌우 기둥과 상부 헤더로 이루어진 `2.22 × 0.20 × 2.55m` 밝은 갈색 목재 U자 포털이 개구부를 감싼다.

### 서쪽 복도와 책상 구역

- 서쪽 복도 중심선은 y=12.2753m, 폭은 1.73m다.
- 끝 벽 <code>Wall_07</code>은 불투명하며 collision을 유지한다.
- 서쪽 두 문 사이의 <code>Table_03</code>은 기존 소파 자리를 대체한다.
- 책상 전면과 약 0.60m를 띄운 위치에 서로 다른 크기의 택배 박스 9개가 5-3-1의 3단으로 쌓여 있다.

### 북측 복도, 통형 포스터와 엘리베이터

<code>GrayPoster_02</code>는 <code>Wall_06</code>에서 코너를 돌아 <code>Wall_05</code>의 첫 번째 엘리베이터 바로 옆까지 이어지는 단일 L자 통형 포스터다.

| 항목 | 값 |
| --- | --- |
| 위치 | (20.5892, 13.0403, 0.85) |
| 방향 | yaw 0°, 로비 -Y 방향 |
| 크기 | 정면 4.5m + 코너 반환부 1.3247m × 높이 1.22m × 두께 0.15m |
| 색상 | (0.34, 0.36, 0.38) 진회색 |
| 구조 | 비발광·watertight L자 <code>PosterSlab</code> Mesh 1개 |
| 물리 | 별도 collider 없음 |

포스터 반환부는 코너에서 `1.3247m` 이어져 첫 번째 엘리베이터 외곽 문틀의 남측 끝 `y=14.365m`에서 맞닿는다. 그 뒤 <code>Wall_05</code>에는 운영 중인 엘리베이터 위치를 나타내는 철문 2개가 있다.

| Prim | 위치 | 크기 | 방향 |
| --- | --- | --- | --- |
| <code>ElevatorDoor_01</code> | (22.8392, 15.2, 0.0) | 1.45 × 2.30 × 0.08m | +X, yaw 90° |
| <code>ElevatorDoor_02</code> | (22.8392, 18.8, 0.0) | 1.45 × 2.30 × 0.08m | +X, yaw 90° |

각 모듈은 브러시드 스테인리스 좌·우 패널, 금속 프레임, 중앙 seam과 점등 상태 표시기로 구성된다. metadata는 <code>operational</code>, 현재 문 상태는 <code>closed</code>다. 시각용 모듈에는 별도 collider를 두지 않고 기존 <code>Wall_05</code> collider를 사용한다.

북측 복도 끝은 <code>Wall_04</code>의 collision을 유지하면서 상부를 통유리로 표현한다. 유리 하단에는 정면 외벽과 같은 높이 `1.02m`의 석재 회색 불투명 벽이 전체 폭 `3.1332m`를 채운다. 그 앞에는 깊이 `0.60m`, 높이 `0.15m`의 낮은 목재 단상 `NorthGlassWoodPlatform`이 있으며 하부벽 남쪽 면과 단상 북쪽 끝이 단차 없이 맞닿는다. 단상 위에는 참고 이미지 형태의 초록색 이동식 안내판 3개가 정면(-Y)을 향해 나란히 놓인다. 각 안내판은 `0.72 × 0.34 × 1.55m`이며 밝은 안내문 면, 초록색 패널, 금속 프레임과 바퀴 4개로 구성된다. 안내판 사이 간격은 `0.23m`, 단상 좌우 끝 여백은 각각 `0.2566m`다. 단상 옆 `ElevatorDoor_02`는 벽을 정면에서 보았을 때 왼쪽으로 `0.20m` 이동했으며 단상과 `0.445m` 떨어져 있다.

### 정문

- 정문은 투명 양개 유리문 2세트, 중앙 고정 유리, 상부 transom으로 구성된다.
- 문 좌우에는 각각 4.85 × 2.82m 통유리가 있다.
- 좌우 통유리 바깥 하단에는 소파 높이에 맞춘 불투명 외벽이 각각 1개씩 있다.
- 왼쪽 외벽은 `Wall_09` 중심선부터 유리문 프레임까지 `5.4055m`, 오른쪽은 유리문 프레임부터 `Wall_11` 중심선까지 `5.1736m`로 이어진다.
- 낮은 외벽은 실제 유리문 구간 `x=21.42–25.58m`를 가리지 않으며 실내 가구의 하단 시야를 차단한다.
- 낮은 외벽의 남쪽 바깥 면은 실제 외관 기준인 정문 양옆 기둥 전면 y=-0.01m와 일치한다. 이전보다 안쪽으로 0.0465m 이동해 외부 돌출 단차를 제거했다.
- 기존 <code>Wall_10</code> collider는 낮은 외벽 내부에서 겹쳐지도록 유지하고 불투명 표면만 숨겼다.
- 정문 안쪽 오른편의 택배 박스 4개는 중앙·왼쪽 통행선 x ≤ 24.4m와 <code>Spawn_South</code>를 침범하지 않는다.
- 유리 밖에는 남쪽·북쪽 대형 보도블럭 slab이 있어 기본 그리드 노출을 막는다.

## 재질과 조명

| 대상 | 재질/색상 | 주요 값 |
| --- | --- | --- |
| 바닥 | Bala White granite texture | roughness 0.24, clearcoat 0.26, 2.4m repeat |
| 천장 | warm white matte | 흰색 유지, roughness 0.78 |
| 벽·기둥 | cool stone gray | (0.50, 0.51, 0.52), roughness 0.72 |
| 정면 낮은 외벽 | wall/column 공용 재질 | 높이 1.02m, 왼쪽 폭 5.4055m, 오른쪽 폭 5.1736m |
| 밝은 포스터 | light gray | (0.70, 0.72, 0.74) |
| 통형 포스터 | dark gray | (0.34, 0.36, 0.38), 두께 0.15m |
| 소파 | brown soft matte upholstery | 공용 furniture material |
| 엘리베이터 | brushed stainless steel | metallic 0.84, roughness 0.28 |
| 이동식 안내판 | deep green + brushed metal | green (0.035, 0.28, 0.14), 바퀴 4개/대 |
| 동쪽 양개문 | warm white + honey-brown wood | door (0.91, 0.92, 0.89), portal (0.52, 0.27, 0.09) |

외곽 벽 12개, 메인 기둥 3개, 정문 기둥 2개와 정면 낮은 외벽 2개는 푸른 기가 아주 약한 석재 회색을 사용한다. 밝은 포스터보다 어둡고 통형 진회색 포스터보다 밝아 세 표면이 구분된다. 바닥과 흰색 천장 재질은 이 색상 조정의 영향을 받지 않는다.

조명 구성:

- 일반 매입형 LED 패널 15개: RectLight intensity 8000
- 중앙 대형 패널 1개: 6.0 × 2.4m, intensity 12000, normalize false
- 추가된 일반 패널 3개: (19.0, 12.0), (28.8, 12.0), (29.0, 6.0)
- DomeLight: intensity 1600, 별도 color 미지정

## 동적 택배 박스

모든 상자는 크기 조합이 서로 다르며 <code>/World/DynamicObstacles</code> 아래에 있다.

| 구역 | 수량 | 적층 | 통행 조건 |
| --- | ---: | --- | --- |
| <code>Table_03</code> 앞 | 9 | 5-3-1, 최대 3단 | 책상 전면과 약 0.60m 간격 |
| 정문 안쪽 오른편 | 4 | 바닥 3 + 상단 1 | 중앙·왼쪽 진입로 보존 |
| 두 엘리베이터 사이 | 3 | 바닥 2 + 상단 1 | 서쪽 벽 쪽 배치, 동쪽 약 2.32m 통행 폭 보존 |

- 전체 질량: 43.9kg
- Root: <code>PhysicsRigidBodyAPI</code>, <code>PhysicsMassAPI</code>
- Body: <code>PhysicsCollisionAPI</code>
- 초기 상태: starts asleep, non-kinematic
- 접촉 후 동적 강체로 반응
- 외관: kraft cardboard 3색, 포장 테이프와 배송 라벨

기존 raw <code>/World/Obstacles</code>는 사용하지 않는다.

## Stage 구조

~~~text
/World
├── PhysicsScene
├── DomeLight
├── Looks
├── Environment
│   ├── Floor
│   ├── Ceiling
│   ├── CeilingLights
│   │   ├── CeilingLight_01 ... CeilingLight_15
│   │   ├── CeilingLight_Central_Large
│   │   └── AirConditioners/CeilingAC_01 ... CeilingAC_02
│   ├── FrontEntranceGlassWalls
│   │   ├── LeftFullHeightGlass/LowerOpaqueWall
│   │   └── RightFullHeightGlass/LowerOpaqueWall
│   ├── NorthCorridorEndGlassWall/LowerOpaqueWall
│   ├── NorthGlassWoodPlatform
│   └── Walls
├── Columns
│   ├── Column_01
│   ├── Column_03
│   ├── Column_02
│   ├── Entrance_Pillar_ATM_Side
│   └── Entrance_Pillar_Opposite
├── Architecture
│   ├── DigitalDisplayWall_01
│   ├── WoodPartition_01
│   ├── ColumnDisplay_01
│   ├── GrayPoster_01
│   ├── GrayPoster_02
│   ├── ElevatorDoor_01
│   ├── ElevatorDoor_02
│   └── GreenInformationBoard_01 ... GreenInformationBoard_03
├── Furniture
│   ├── Sofa_02, Sofa_03, Sofa_05
│   ├── Sofa_Corner_01
│   ├── Sofa_U_Column_02
│   ├── ATM_01, ATM_02
│   └── Table_01 ... Table_03
├── DynamicObstacles
│   └── ParcelBox_01 ... ParcelBox_16
├── Doors
└── SpawnPoints
~~~

## 설정 파일과 생성 layer

배치값은 JSON에서 수정하고 생성 USD layer는 스크립트로 다시 만든다.

| 대상 | 원본 설정 | 생성 layer | 생성 스크립트 |
| --- | --- | --- | --- |
| 문 | <code>config/doors.json</code> | <code>config/doors_layout.usda</code> | <code>update_cbnu_haksan_doors.py</code> |
| 가구 | <code>config/furniture.json</code> | <code>config/furniture_layout.usda</code> | <code>update_cbnu_haksan_furniture.py</code> |
| 택배 박스 | <code>config/dynamic_obstacles.json</code> | <code>config/dynamic_obstacles_layout.usda</code> | <code>update_cbnu_haksan_dynamic_obstacles.py</code> |
| 천장 조명·에어컨 | <code>config/ceiling.json</code> | <code>config/ceiling_layout.usda</code> | <code>update_cbnu_haksan_ceiling.py</code> |
| 전시·포스터·엘리베이터 | <code>config/architecture.json</code> | <code>config/architecture_layout.usda</code> | <code>update_cbnu_haksan_architecture.py</code> |

표의 <code>config/</code> 경로는 <code>worlds/cbnu_haksan_1f_corridor/</code> 기준이며 생성 스크립트는 저장소의 <code>scripts/</code>에 있다.

전체 재생성:

~~~bash
cd /home/a/Isaac_Worlds
python3 scripts/update_cbnu_haksan_doors.py
python3 scripts/update_cbnu_haksan_furniture.py
python3 scripts/update_cbnu_haksan_dynamic_obstacles.py
python3 scripts/update_cbnu_haksan_ceiling.py
python3 scripts/update_cbnu_haksan_architecture.py
MPLCONFIGDIR=/tmp/cbnu_matplotlib python3 scripts/render_cbnu_haksan_preview.py
~~~

생성된 <code>*_layout.usda</code>는 직접 수정하지 않는다.

## 주요 수정 지점

### 전시 구조, 포스터와 엘리베이터

배치·크기·상태:

<code>worlds/cbnu_haksan_1f_corridor/config/architecture.json</code>

형상:

~~~text
assets/architecture/digital_display_wall/
assets/architecture/wall_decor/
assets/architecture/elevators/stainless_elevator_door.usda
~~~

### 조명과 천장형 에어컨

- 배치: <code>worlds/cbnu_haksan_1f_corridor/config/ceiling.json</code>
- 일반 패널: <code>assets/architecture/ceiling/ceiling_panel_light.usda</code>
- 중앙 대형 패널: <code>assets/architecture/ceiling/ceiling_panel_light_large.usda</code>
- 4방향 카세트 에어컨: <code>assets/architecture/ceiling/ceiling_cassette_air_conditioner.usda</code>

중앙 대형 패널의 좌우에는 `CeilingAC_01`, `CeilingAC_02`가 중앙축 기준으로 대칭 배치되어 있다. 각 장치는 1.1 × 1.1m이며 대형 조명 가장자리와 0.65m 간격을 유지한다. 흡입 그릴과 4방향 토출구를 가지며 별도 조명이나 collider는 추가하지 않는다.

천장 본체의 높이와 footprint는 조명 config만으로 자동 재생성되지 않는다. 이를 바꿀 때는 <code>geometry.json</code>과 기준 Stage의 <code>Ceiling</code> Mesh를 함께 수정한다.

### 가구와 소파 Mesh

- 배치: <code>worlds/cbnu_haksan_1f_corridor/config/furniture.json</code>
- 직선 소파 재질: <code>assets/materials/furniture/brown_sofa_material.usda</code>
- 코너/U형 소파 재질: <code>assets/materials/furniture/dark_reddish_brown_leather_material.usda</code>
- Corner/U형 통합 Mesh 생성: <code>scripts/generate_unified_sofa_meshes.py</code>

Corner/U형의 보이는 형상은 각각 하나의 <code>SofaUnified</code> Mesh다. 생성 스크립트는 render Mesh만 갱신하며 invisible collision helper와 상대경로 material reference는 유지한다.

### 복도, 벽과 기둥

<code>worlds/cbnu_haksan_1f_corridor/config/geometry.json</code>은 기준 수치를 기록하지만 메인 geometry를 자동 생성하지 않는다. 복도 polygon, Floor/Ceiling point, 벽 또는 기둥 위치를 바꾸면 기준 Stage와 관련 배치 config를 함께 수정해야 한다.

<code>column_2m.usda</code>와 <code>wall_column_light_gray.usda</code>는 기존 reference 호환을 위해 파일명을 유지한다. 현재 실제 기둥 단면은 1.2 × 1.2m이고 표면은 중간 회색이다.

## Collision 정책

- Floor, Ceiling, 외곽 Wall: collision enabled
- 동적 택배 박스: rigid body + mass + 단일 box collider
- 기존 L자 전시벽: invisible box helper 2개
- 개별 화면과 두 포스터: 별도 collider 없음
- 엘리베이터 철문: 별도 collider 없음, <code>Wall_05</code> 재사용
- 정문 유리 구조: 별도 collider 없음, <code>Wall_10</code> 재사용
- 정면 낮은 외벽 2개: 별도 collider 없음, <code>Wall_10</code> 재사용
- 북측 끝 통유리: 별도 collider 없음, <code>Wall_04</code> 재사용
- 북측 통유리 앞 목재 단상: 단일 static box collider
- 정문 측면 기둥: 시각용, 기존 남쪽 벽 collider 사용

## 검증

~~~bash
cd /home/a/Isaac_Worlds
python3 scripts/validate_cbnu_haksan_detail.py
./scripts/test_world_with_isaac_usd.sh
~~~

2026-09-04 Asia/Seoul 기준:

~~~text
CBNU Haksan detailed lobby validation: PASS
USD references: 83 relative and resolved
CBNU Haksan composed Stage: PASS (USD 24.05)
verified composed prims: 77
preview: 2250 × 1425
architecture preview: 2250 × 1425
~~~

검증기는 geometry, material binding, collision, 조명 수량과 좌표, 가구·문 배치, 정면 낮은 외벽, 북측 통유리 앞 목재 단상, 포스터 치수, 엘리베이터 두 대, 택배 박스 적층과 모든 상대경로 reference를 확인한다.

## 저장소 구조

~~~text
Isaac_Worlds/
├── assets/
│   ├── architecture/
│   │   ├── ceiling/
│   │   ├── digital_display_wall/
│   │   ├── doors/
│   │   ├── elevators/
│   │   ├── exterior/
│   │   ├── wall_decor/
│   │   └── windows/
│   ├── equipment/
│   ├── furniture/
│   ├── materials/
│   └── structural/
├── worlds/cbnu_haksan_1f_corridor/
│   ├── cbnu_haksan_1f_corridor.usda
│   ├── config/
│   ├── reference/
│   └── preview_*.png
├── scripts/
├── terrains/
└── docs/
~~~

## 현재 범위

포함:

- 로비·복도 시각 구성과 collision
- 정적 가구·문·엘리베이터 입구
- 동적 택배 박스 장애물
- 조명, 유리, 바닥과 외부 보도블럭
- 결정론적 평면 미리보기와 정적/실제 USD 검증

미포함:

- Go2 spawn과 RL policy 연결
- reward, observation, action 변경
- 엘리베이터 이동과 문 개폐 animation
- 실측 기반 치수 보증
- terrain 생성과 물리 parameter tuning
