# 派車系統（Dispatch System）

此專案提供一個以 Python 撰寫的輕量派車系統，能夠管理車輛、司機與乘車需求，並依據車輛容量與距離自動指派最合適的司機。系統以 JSON 檔案作為儲存層，適合在小型團隊或 PoC 階段快速驗證派車流程。

## 核心能力

- **車輛管理**：紀錄車輛容量與目前座標，可更新定位或停用車輛。
- **司機管理**：維護司機與所屬車輛的關聯，追蹤是否可接單。
- **乘車需求管理**：建立、取消、完成乘車需求並追蹤狀態。
- **派遣邏輯**：找出容量足夠且可用的司機，依據距離（假設原點為派遣中心）進行排序後派遣。
- **CLI 操作**：透過命令列即可新增資料與派遣，輸出結果為 JSON 方便整合。

## 專案結構

```
├── dispatch
│   ├── cli.py        # 命令列介面
│   ├── models.py     # 車輛、司機、乘車需求等資料模型
│   ├── service.py    # 派車商業邏輯
│   └── storage.py    # JSON 儲存層
├── tests
│   └── test_dispatch.py
└── README.md
```

## 安裝與需求

- Python 3.11+
- 不需額外套件（僅使用標準函式庫）。

## 執行範例

```bash
# 建立虛擬環境（可選）
python -m venv .venv
source .venv/bin/activate

# 新增車輛與司機
python -m dispatch.cli add-vehicle V001 4 "25.04,121.56"
python -m dispatch.cli add-driver D001 Alice V001

# 建立乘車需求
python -m dispatch.cli request R001 3 "25.05,121.57" "25.03,121.50"

# 派遣
python -m dispatch.cli dispatch R001
```

輸出範例：

```json
{
  "status": "assigned",
  "request": "R001",
  "driver": "D001",
  "vehicle": "V001",
  "distance": 1.41
}
```

## 測試

```bash
python -m pytest
```
