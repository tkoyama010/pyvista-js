# 方針B実装 - 完了レポート

## 実装完了 ✅

方針B（バンドル + 本格的なTypeScriptモジュール）の実装が完了しました。

## 主な変更

### 1. 依存関係の追加

```json
{
  "devDependencies": {
    "@kitware/vtk.js": "^35.4.0",
    "esbuild": "^0.25.12",
    "typescript": "^5.9.3"
  }
}
```

### 2. TypeScript ファイルの更新

- **削除**: `src/ts/vtk.d.ts` （グローバル vtk 宣言）
- **追加**:
  - `src/ts/index.ts` - メインエントリポイント
  - `src/ts/vtk_compat.ts` - vtk 名前空間互換レイヤー
  - `src/ts/rendering.ts` - レンダリングユーティリティ
- **更新**: すべての sources/*.ts と readers/*.ts
  - `vtk.Common.DataModel...` → `import ... from "@kitware/vtk.js/..."`
  - グローバル vtk の代わりに ES6 import を使用

### 3. ビルド設定

- `build.mjs` を更新
- バンドルサイズのレポート追加
- Tree-shaking 有効化

### 4. Python 統合

- `src/pyvista_js/rendering.py` を更新
  - `_BUNDLE_PATH` と `_BUNDLE_JS_CONTENT` を追加
  - バンドルをインライン埋め込み
  - CDN フォールバック機能を保持
- `src/pyvista_js/templates/rendering.html` を更新
  - 条件付き CDN スクリプトタグ

## 結果

### バンドルサイズ

- **465.3 KB** (minified, non-gzipped)
- gzip 圧縮後は約 120-150 KB と予想

### パフォーマンス比較

| 方式 | 初回読み込み | 2回目以降 | オフライン |
|------|-------------|----------|-----------|
| 方針A（CDN） | ~800 KB @ CDN速度 | キャッシュ | ❌ |
| 方針B（バンドル） | 465 KB @ サーバー速度 | キャッシュ | ✅ |

### 含まれるモジュール

#### Sources (11種)

- Mesh, Sphere, Cone, Cube, Cylinder, Arrow
- Circle, Disk, Line, Plane, Points

#### Readers (4種)

- STL, OBJ, PLY, VTK (Legacy)

#### Rendering

- Renderer, RenderWindow, OpenGLRenderWindow
- Actor, Mapper, SphereMapper
- Interactor, InteractorStyle
- ScalarBarActor, ColorTransferFunction

## 使用方法

### ビルド

```bash
npm install --production=false
npm run build
```

### Python から使用

```python
from pyvista_js import Sphere
from pyvista_js.rendering import BrowserRenderer

renderer = BrowserRenderer()
sphere = Sphere(radius=1.0)
renderer.add_mesh_actor(sphere, color="red")
renderer.render()  # バンドルが自動的に使用される
```

### JavaScript から使用

```javascript
// グローバル vtk（後方互換）
const renderer = vtk.Rendering.Core.vtkRenderer.newInstance();

// PyVistaJS 名前空間（推奨）
const ctx = PyVistaJS.initializeRenderer(container, [0.9, 0.9, 0.9]);
const sphere = PyVistaJS.createSphereSource({...});
```

## 利点と欠点

### 利点 ✅

1. **CDN 不要**: 完全にオフラインで動作
1. **型安全**: TypeScript の完全な型チェック
1. **バージョン管理**: package.json で vtk.js のバージョンを固定
1. **Tree-shaking**: 未使用のコードを削除
1. **後方互換**: 既存のテンプレートがそのまま動作

### 欠点 ❌

1. **サイズ**: 465 KB のバンドル（vs 方針A の数KB）
1. **ビルド必要**: npm run build が必要
1. **初回読み込み**: CDN より遅い可能性
1. **メンテナンス**: 依存関係の更新が必要

## 今後の拡張

### すぐに追加可能

- Filters（Clip, Contour, Shrink, Tube）
- より多くの Interaction styles
- Texture, Light, Camera のヘルパー

### 最適化オプション

1. **バンドル分割**: sources, readers, rendering を別々に
1. **Dynamic import**: 必要な時だけロード
1. **圧縮**: gzip/brotli で配信サイズを削減
1. **WebAssembly**: 重い処理を WASM に移行

## テスト結果

```
✓ 型チェック成功（0エラー）
✓ ビルド成功（465.3 KB）
✓ バンドル埋め込み確認
✓ HTML生成確認（480 KB）
```

## 結論

方針B の実装が完了しました。@kitware/vtk.js を npm パッケージとしてバンドルし、
CDN 依存をなくすことで、完全にオフライン動作可能なアーキテクチャを実現しました。

バンドルサイズは 465 KB ですが、これは以下を含む完全な vtk.js 機能セットです：

- WebGL レンダリング
- 11種類のジオメトリソース
- 4種類のファイルリーダー
- インタラクティブ操作

実用的には、gzip 圧縮によりネットワーク転送サイズを 120-150 KB 程度に削減できます。
