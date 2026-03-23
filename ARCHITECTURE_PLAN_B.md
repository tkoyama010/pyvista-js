# 方針B実装: バンドル + 本格的なTypeScriptモジュール

## 概要
@kitware/vtk.js を npm パッケージとしてインストールし、esbuild でバンドルする重量級アプローチを実装しました。

## 実装内容

### 1. TypeScript モジュール化
- すべての sources と readers を `@kitware/vtk.js` から直接インポート
- グローバルな `vtk` 変数への依存を削除
- 型安全性の向上（vtk.d.ts を削除）

### 2. バンドル構成
- **Entry Point**: `src/ts/index.ts`
- **Build Tool**: esbuild
- **Format**: IIFE（即時実行関数式）
- **Global Name**: `PyVistaJS`
- **Output**: `src/pyvista_js/static/pyvista_js.js`

### 3. バンドルサイズ
- **合計サイズ**: 465 KB（minified）
- **内訳**:
  - vtk.js コアモジュール
  - Sources（sphere, cone, cube, etc.）
  - Readers（STL, OBJ, PLY, VTK）
  - Rendering utilities

### 4. 後方互換性
- `vtk_compat.ts` で vtk 名前空間を再構築
- `window.vtk` をグローバルに設定し、既存テンプレートと互換性を保持
- Python テンプレート（rendering.html）は変更不要

### 5. Python 統合
- `rendering.py` を更新してバンドルを優先使用
- CDN フォールバック機能を保持
- `_BUNDLE_JS_CONTENT` でバンドルをインライン化

## ファイル構造

```
src/ts/
├── index.ts                 # メインエントリポイント
├── vtk_compat.ts           # vtk 名前空間互換レイヤー
├── rendering.ts            # レンダリングユーティリティ
├── sources/                # 各種ソース（11ファイル）
│   ├── mesh_source.ts
│   ├── sphere_source.ts
│   └── ...
└── readers/                # 各種リーダー（4ファイル）
    ├── stl_reader.ts
    └── ...
```

## ビルド方法

```bash
npm install --production=false
npm run typecheck  # 型チェック
npm run build      # バンドル生成
```

## 使用方法

### グローバル vtk オブジェクト（後方互換）
```javascript
const renderer = vtk.Rendering.Core.vtkRenderer.newInstance();
```

### PyVistaJS 名前空間（新規）
```javascript
const ctx = PyVistaJS.initializeRenderer(container, [0.9, 0.9, 0.9]);
const sphere = PyVistaJS.createSphereSource({ ... });
const actor = PyVistaJS.createActor(sphere.source);
```

## 利点
- ✅ CDN 依存なし（オフライン動作可能）
- ✅ 型安全性の向上
- ✅ Tree-shaking によるサイズ最適化
- ✅ バージョン管理が容易
- ✅ 既存テンプレートとの互換性

## 欠点
- ❌ バンドルサイズが大きい（465 KB）
- ❌ 初回読み込み時間の増加
- ❌ ビルドプロセスが必要

## 比較

| 項目 | 方針A（CDN） | 方針B（バンドル） |
|------|-------------|-----------------|
| バンドルサイズ | 数KB | 465 KB |
| 初回読み込み | 高速（CDN） | 遅い |
| オフライン | ❌ | ✅ |
| 型安全性 | any | 完全な型 |
| メンテナンス | 容易 | 要ビルド |

## 今後の改善
1. さらに多くの vtk モジュールを vtk_compat.ts に追加
2. フィルタ（clip, contour, shrink, tube）のサポート
3. テクスチャ、ライト、環境マップのサポート
4. バンドル分割による初回読み込みの最適化
