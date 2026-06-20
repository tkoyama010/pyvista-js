# Changelog

## [0.14.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.13.0...pyvista-js-v0.14.0) (2026-06-20)


### Features

* add intro.ipynb notebook and update ReadTheDocs config for JupyterLite ([#432](https://github.com/tkoyama010/pyvista-js/issues/432)) ([4a1e97e](https://github.com/tkoyama010/pyvista-js/commit/4a1e97e0a23be896ed94326c42e6b28867ff0fcb))
* add triangulate filter using vtk.js TriangleFilter ([#413](https://github.com/tkoyama010/pyvista-js/issues/413)) ([a43ec9b](https://github.com/tkoyama010/pyvista-js/commit/a43ec9b45d9eba397fa5f34cea208fc354e3b1d7))
* add upper bound constraints to dependencies ([#417](https://github.com/tkoyama010/pyvista-js/issues/417)) ([17197e3](https://github.com/tkoyama010/pyvista-js/commit/17197e3a04e9f72405ccfd05312991c665650abc))
* add uv-lock workflow from pyvista-wasm ([#421](https://github.com/tkoyama010/pyvista-js/issues/421)) ([03ee6aa](https://github.com/tkoyama010/pyvista-js/commit/03ee6aa89313af4210a754348f4df1ec4fcba024))
* Update Try Lite Now link to ReadTheDocs and remove JupyterLite deploy action ([#433](https://github.com/tkoyama010/pyvista-js/issues/433)) ([de7e3d1](https://github.com/tkoyama010/pyvista-js/commit/de7e3d1c55040666c1a66c5b3c762048ee146f02))


### Bug Fixes

* add upper bound to requires-python to prevent uv-lock failure ([#505](https://github.com/tkoyama010/pyvista-js/issues/505)) ([6c077ce](https://github.com/tkoyama010/pyvista-js/commit/6c077ce3c8390df57c75cc003d3ce0b651eb2a05))
* **deps:** upgrade gitpython to 3.1.49 to fix GHSA-rpm5-65cw-6hj4 ([#460](https://github.com/tkoyama010/pyvista-js/issues/460)) ([7565220](https://github.com/tkoyama010/pyvista-js/commit/756522086d81863e47429002f16e4247a10c86d6))
* **deps:** upgrade Pygments to 2.20.0 to fix CVE-2026-4539 ([#461](https://github.com/tkoyama010/pyvista-js/issues/461)) ([1c53e18](https://github.com/tkoyama010/pyvista-js/commit/1c53e189f7093bc6621d12883ec195e3e15e5987))
* handle TypeError from Pyodide proxy creation in JupyterLite ([#503](https://github.com/tkoyama010/pyvista-js/issues/503)) ([d06fed3](https://github.com/tkoyama010/pyvista-js/commit/d06fed3bc01810626bc7295da80b813eebce3263))
* improve stlite preview capture reliability ([#412](https://github.com/tkoyama010/pyvista-js/issues/412)) ([81f00f5](https://github.com/tkoyama010/pyvista-js/commit/81f00f569de348a89616ab106370c04f380287f2))
* resolve mypy type errors for _scene_data parameter ([#411](https://github.com/tkoyama010/pyvista-js/issues/411)) ([be26dee](https://github.com/tkoyama010/pyvista-js/commit/be26dee74ef5f0cd86b553352bc0896b3840a692))


### Continuous Integration

* resolve lint errors by updating to fixed codebase ([16575dc](https://github.com/tkoyama010/pyvista-js/commit/16575dc25fcb4ab96dd5dcc97d931cbed63bd987))

## [0.13.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.12.0...pyvista-js-v0.13.0) (2026-03-30)

### Features

- add fill_holes filter to PolyData ([#394](https://github.com/tkoyama010/pyvista-js/issues/394)) ([cfeb115](https://github.com/tkoyama010/pyvista-js/commit/cfeb1156683cf209fa83be2ac532d9543a625224))
- add Notebook.link configuration ([#385](https://github.com/tkoyama010/pyvista-js/issues/385)) ([1d09838](https://github.com/tkoyama010/pyvista-js/commit/1d09838f651e7bae02f79425e777394fca60088e))
- add UnstructuredGrid and CellType for 3D cell support ([#396](https://github.com/tkoyama010/pyvista-js/issues/396)) ([320c289](https://github.com/tkoyama010/pyvista-js/commit/320c2898d7c4cf4cfce2a2fd77937fef55cca24d))

### Bug Fixes

- migrate xo config to xo.config.js for xo 2.x compatibility (fixes [#381](https://github.com/tkoyama010/pyvista-js/issues/381)) ([#384](https://github.com/tkoyama010/pyvista-js/issues/384)) ([43c5e5f](https://github.com/tkoyama010/pyvista-js/commit/43c5e5f9fd0e6ff6e4c0e6b56ca1202207f536b6))

### Documentation

- replace stlite GitHub Pages URL with edit.share.stlite.net share URL ([#386](https://github.com/tkoyama010/pyvista-js/issues/386)) ([1f3d6f1](https://github.com/tkoyama010/pyvista-js/commit/1f3d6f107446379b80bfb872a684ee4107df8905))

### Continuous Integration

- use PAT for Release Please to set PR author ([#388](https://github.com/tkoyama010/pyvista-js/issues/388)) ([7e65a00](https://github.com/tkoyama010/pyvista-js/commit/7e65a00b81bca085e9fff1ee7a830d3b87a13639))

## [0.12.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.11.0...pyvista-js-v0.12.0) (2026-03-24)

### Features

- add capture-stlite-preview CLI command and stlite preview to README ([#328](https://github.com/tkoyama010/pyvista-js/issues/328)) ([63e0c27](https://github.com/tkoyama010/pyvista-js/commit/63e0c278142338ce196a072876e79d2ebe4d645c))
- add CLI options to save screenshot output ([#312](https://github.com/tkoyama010/pyvista-js/issues/312)) ([df65ae9](https://github.com/tkoyama010/pyvista-js/commit/df65ae93a44f03947b45b000976ad3cc77d98644))
- add Lucy Angel example with custom lighting and binary PLY support ([#324](https://github.com/tkoyama010/pyvista-js/issues/324)) ([fb4f281](https://github.com/tkoyama010/pyvista-js/commit/fb4f2818bffed1f5e510534e6cd95261863668aa))
- add relative camera movement CLI options ([#347](https://github.com/tkoyama010/pyvista-js/issues/347)) ([217bb04](https://github.com/tkoyama010/pyvista-js/commit/217bb04627c727c3bc5c4b437fe3ac3743859459))
- move stlite demo from ReadTheDocs to GitHub Pages ([#325](https://github.com/tkoyama010/pyvista-js/issues/325)) ([3cc3c01](https://github.com/tkoyama010/pyvista-js/commit/3cc3c01f02fef6c8074c9dda8aeea2f536633f81))
- separate HTML templates and TS logic with Prettier formatting ([#338](https://github.com/tkoyama010/pyvista-js/issues/338)) ([36690d8](https://github.com/tkoyama010/pyvista-js/commit/36690d8036860e121181d3ffac35fb4c0e713e48))

### Bug Fixes

- add playwright and pillow dependencies to nightly workflow ([#340](https://github.com/tkoyama010/pyvista-js/issues/340)) ([c1cf78d](https://github.com/tkoyama010/pyvista-js/commit/c1cf78d99af9a3b6f2bf3ded16a8dababaedc51a))
- align nightly workflow with Python >=3.12 requirement ([#343](https://github.com/tkoyama010/pyvista-js/issues/343)) ([199798d](https://github.com/tkoyama010/pyvista-js/commit/199798d4956b22744e7efce1b4baa5e06bdb76c9))
- increase timeouts for stlite demo capture to handle slow loading ([#344](https://github.com/tkoyama010/pyvista-js/issues/344)) ([f163af5](https://github.com/tkoyama010/pyvista-js/commit/f163af56c1527746b41de75468de54f307da3f85))
- increase timeouts for stlite preview capture ([#337](https://github.com/tkoyama010/pyvista-js/issues/337)) ([f42a192](https://github.com/tkoyama010/pyvista-js/commit/f42a19254ef9229c1753dd98280372af2330ac6f))
- install playwright dependencies in nightly tests ([#341](https://github.com/tkoyama010/pyvista-js/issues/341)) ([8f25f4d](https://github.com/tkoyama010/pyvista-js/commit/8f25f4d6884fc228ec350857d96a27e75bf16d68))
- search iframes for canvas in stlite demo capture ([#346](https://github.com/tkoyama010/pyvista-js/issues/346)) ([f0b6199](https://github.com/tkoyama010/pyvista-js/commit/f0b619979ebd6183a79fb8ca79a49cf2630403e0))
- update nightly test workflow to match minimum Python version ([#342](https://github.com/tkoyama010/pyvista-js/issues/342)) ([6d4baa5](https://github.com/tkoyama010/pyvista-js/commit/6d4baa52b787434b3c3b51a066d7352571fc985f))

### Reverts

- separate HTML templates and TS logic with Prettier formatting ([#338](https://github.com/tkoyama010/pyvista-js/issues/338)) ([#365](https://github.com/tkoyama010/pyvista-js/issues/365)) ([27adbcf](https://github.com/tkoyama010/pyvista-js/commit/27adbcf4b928680ad545e60ead3c5f9e8ecd8ac5))

### Documentation

- add tkoyama010 as a contributor for projectManagement ([#345](https://github.com/tkoyama010/pyvista-js/issues/345)) ([0e723b6](https://github.com/tkoyama010/pyvista-js/commit/0e723b682abfa1fb78b1fb8f63fd361058edc041))
- replace doctoc with mdformat-toc for TOC generation ([#348](https://github.com/tkoyama010/pyvista-js/issues/348)) ([5b4dfcc](https://github.com/tkoyama010/pyvista-js/commit/5b4dfcc3b39931947096d904d9d4f11339ef74af))
- update Light class docstring to match PyVista style ([#372](https://github.com/tkoyama010/pyvista-js/issues/372)) ([1620f27](https://github.com/tkoyama010/pyvista-js/commit/1620f27b495499068fd5d2c50341f22e13514c8c))
- update Scientific Python Standards section with badges ([#330](https://github.com/tkoyama010/pyvista-js/issues/330)) ([7321805](https://github.com/tkoyama010/pyvista-js/commit/7321805b1c4b1cf373cf3af1bd68a82d70d79a2e))
- Updates for project pyvista-js-doc and language ja ([#329](https://github.com/tkoyama010/pyvista-js/issues/329)) ([944eb71](https://github.com/tkoyama010/pyvista-js/commit/944eb71bc0dc5408acec24f5fa9d260339d48519))
- Updates for project pyvista-js-doc and language ja ([#370](https://github.com/tkoyama010/pyvista-js/issues/370)) ([23faacd](https://github.com/tkoyama010/pyvista-js/commit/23faacd50755fd66dfff347bdc342d33dab68161))

### Continuous Integration

- upload preview GIFs to GitHub Releases instead of storing in repo ([#376](https://github.com/tkoyama010/pyvista-js/issues/376)) ([240ed9e](https://github.com/tkoyama010/pyvista-js/commit/240ed9e6ab7045f2bac1cb66aa16651872e31c94))

## [0.11.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.10.0...pyvista-js-v0.11.0) (2026-03-22)

### Features

- Add Camera.elevation property ([#302](https://github.com/tkoyama010/pyvista-js/issues/302)) ([722f145](https://github.com/tkoyama010/pyvista-js/commit/722f145ef071689bea287baaafa183ddd0bd47b0))
- add Plotter.add_points() method for point cloud rendering ([#170](https://github.com/tkoyama010/pyvista-js/issues/170)) ([df86e9a](https://github.com/tkoyama010/pyvista-js/commit/df86e9a197a9c6bafbbcf1d9b41a23c9b858077d))
- add smooth_shading option to add_mesh() ([#245](https://github.com/tkoyama010/pyvista-js/issues/245)) ([e3a312e](https://github.com/tkoyama010/pyvista-js/commit/e3a312e542636a1e2ce4dfe2b0c23653ff2cb181))

### Bug Fixes

- remove unsupported \<path> placeholder from translation_files_expression ([#293](https://github.com/tkoyama010/pyvista-js/issues/293)) ([4571cbb](https://github.com/tkoyama010/pyvista-js/commit/4571cbb601d5c5f153bff3f5ba446878d7a9f4e0))
- replace source_file with source_file_dir in transifex.yml ([#290](https://github.com/tkoyama010/pyvista-js/issues/290)) ([0a18589](https://github.com/tkoyama010/pyvista-js/commit/0a18589e1ee457f3c0bc53414e0e51a341ee97db))

### Documentation

- add comprehensive CONTRIBUTING.md file ([#315](https://github.com/tkoyama010/pyvista-js/issues/315)) ([8f991e1](https://github.com/tkoyama010/pyvista-js/commit/8f991e1d25c3fa035a2dfd96074693543a45d349))
- add doctoc to pre-commit hooks ([#319](https://github.com/tkoyama010/pyvista-js/issues/319)) ([7a18a42](https://github.com/tkoyama010/pyvista-js/commit/7a18a42678f97261e3d451eabf0ad18a454ba759))
- add GitHub issue templates for bug reports, features, and documentation ([#316](https://github.com/tkoyama010/pyvista-js/issues/316)) ([3b74547](https://github.com/tkoyama010/pyvista-js/commit/3b74547c7e94105f72e11a12b13c9d2724b1c214))
- add GitHub Sponsors link ([#289](https://github.com/tkoyama010/pyvista-js/issues/289)) ([0c146ae](https://github.com/tkoyama010/pyvista-js/commit/0c146ae122fe2d2c097a4676672d477cd6462c1c))
- add pull request template ([#317](https://github.com/tkoyama010/pyvista-js/issues/317)) ([7ed8180](https://github.com/tkoyama010/pyvista-js/commit/7ed818029ce55a74870175d9bf8d915b880b59b7))
- add SPEC-0004 (Nightly Tests) badge to README ([#311](https://github.com/tkoyama010/pyvista-js/issues/311)) ([dd6702c](https://github.com/tkoyama010/pyvista-js/commit/dd6702c89c50d951ff8b0edf1788f1fba1a57219))
- add tkoyama010 as a contributor for platform ([#310](https://github.com/tkoyama010/pyvista-js/issues/310)) ([9bb1ef7](https://github.com/tkoyama010/pyvista-js/commit/9bb1ef77a283ca4902a8324938e4e153e43abc2c))
- add tkoyama010 as a contributor for translation ([#299](https://github.com/tkoyama010/pyvista-js/issues/299)) ([804028c](https://github.com/tkoyama010/pyvista-js/commit/804028c39da08361c42d9898985fa96026681f82))
- add transifex as a contributor for doc, and translation ([#300](https://github.com/tkoyama010/pyvista-js/issues/300)) ([05d2e20](https://github.com/tkoyama010/pyvista-js/commit/05d2e202388202fc63c8e2c23bf9bc82c4b735a7))
- move badges from README.md to corresponding sections ([#320](https://github.com/tkoyama010/pyvista-js/issues/320)) ([65b80a1](https://github.com/tkoyama010/pyvista-js/commit/65b80a175e4c12361804b4ee25966738b3aaafa8))
- reorganize badges in README.md to related sections ([#314](https://github.com/tkoyama010/pyvista-js/issues/314)) ([1727967](https://github.com/tkoyama010/pyvista-js/commit/1727967dc7d360ca385f8e0fb866a49a07fdbd07))
- reorganize badges to related documentation files ([#313](https://github.com/tkoyama010/pyvista-js/issues/313)) ([440398a](https://github.com/tkoyama010/pyvista-js/commit/440398a8a5924c6e39b1de9e8c16425fd00c5bf9))
- Updates for file docs/pot/cli/plot.pot in ja [Manual Sync] ([#294](https://github.com/tkoyama010/pyvista-js/issues/294)) ([4b4b7ed](https://github.com/tkoyama010/pyvista-js/commit/4b4b7ed5891e4d7ae39556ae6502674a5bd26844))
- Updates for project pyvista-js and language ja ([#298](https://github.com/tkoyama010/pyvista-js/issues/298)) ([93070dc](https://github.com/tkoyama010/pyvista-js/commit/93070dc6a0612b43983e4542a8513b3adbbc70cb))
- Updates for project pyvista-js-doc and language ja ([#305](https://github.com/tkoyama010/pyvista-js/issues/305)) ([fd05db4](https://github.com/tkoyama010/pyvista-js/commit/fd05db44646adf3402807a526f90d987905d87c0))

### Continuous Integration

- use transifex-integration[bot] as commit author in Transifex workflow ([#304](https://github.com/tkoyama010/pyvista-js/issues/304)) ([d6230e8](https://github.com/tkoyama010/pyvista-js/commit/d6230e81a94d4f1638727398c939780be045aec4))

## [0.10.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.9.1...pyvista-js-v0.10.0) (2026-03-21)

### Features

- add contour filter to PolyData ([#167](https://github.com/tkoyama010/pyvista-js/issues/167)) ([9bdf2ce](https://github.com/tkoyama010/pyvista-js/commit/9bdf2ced8b5fda95f899a41f4c8aff41f4d8e8ec))
- add i18n documentation support using Sphinx i18n feature ([#213](https://github.com/tkoyama010/pyvista-js/issues/213)) ([af02e6a](https://github.com/tkoyama010/pyvista-js/commit/af02e6a036a4f77a74d6330b22c1e13b094dc11c))
- add Playwright integration for headless browser testing ([#253](https://github.com/tkoyama010/pyvista-js/issues/253)) ([0a14929](https://github.com/tkoyama010/pyvista-js/commit/0a1492943dbf50e379bffa8ed1794e603ccdcc44))
- add Plotter.screenshot() method for capturing rendered scenes ([#276](https://github.com/tkoyama010/pyvista-js/issues/276)) ([8135a93](https://github.com/tkoyama010/pyvista-js/commit/8135a933340f89751a39b36c3dccb38ebe7af62e))
- add SPEC-0008 compliance for secure release process ([#270](https://github.com/tkoyama010/pyvista-js/issues/270)) ([6fbf589](https://github.com/tkoyama010/pyvista-js/commit/6fbf5893296e84a97a5c4f756dd50afedc1ecbdc))
- Add Text class for 2D text annotations ([#235](https://github.com/tkoyama010/pyvista-js/issues/235)) ([79be237](https://github.com/tkoyama010/pyvista-js/commit/79be237585151d51f834e69c94dd89df906e5778))
- add transifex.yml for GitHub App integration ([#288](https://github.com/tkoyama010/pyvista-js/issues/288)) ([dc09df6](https://github.com/tkoyama010/pyvista-js/commit/dc09df6834121ecbb505f7a39601f111fdd45fa5))
- adopt SPEC 0001 for lazy loading of submodules ([#266](https://github.com/tkoyama010/pyvista-js/issues/266)) ([e63dff1](https://github.com/tkoyama010/pyvista-js/commit/e63dff1857dfc2a5b4e5391a96e50d56fe50e844))
- use Stanford Bunny as default object in stlite demo ([#278](https://github.com/tkoyama010/pyvista-js/issues/278)) ([2f21c40](https://github.com/tkoyama010/pyvista-js/commit/2f21c405f50605bf5b75cf3ce1ac96e2716d7def))

### Bug Fixes

- install lazy-loader in JupyterLite preamble to fix Try it examples ([#272](https://github.com/tkoyama010/pyvista-js/issues/272)) ([f654420](https://github.com/tkoyama010/pyvista-js/commit/f654420cde488f1699ab6286f497ca2e810da255))
- replace tx add bulk with dynamic config generation and direct push ([#285](https://github.com/tkoyama010/pyvista-js/issues/285)) ([36b1c3e](https://github.com/tkoyama010/pyvista-js/commit/36b1c3ebb3dbef542e28d8d74063040c38ec6d85))
- use tx add bulk to register Transifex resources dynamically ([#281](https://github.com/tkoyama010/pyvista-js/issues/281)) ([65eaf5a](https://github.com/tkoyama010/pyvista-js/commit/65eaf5a4b47709d0e32f65b35bc4dc75b74684b3))

### Documentation

- add SPEC 6 compliance for upper bound constraints ([#268](https://github.com/tkoyama010/pyvista-js/issues/268)) ([baf47b8](https://github.com/tkoyama010/pyvista-js/commit/baf47b8702b04fe444380cae1a9278aedca09253))
- add SPEC 7 compliance documentation ([#269](https://github.com/tkoyama010/pyvista-js/issues/269)) ([fdd5a3d](https://github.com/tkoyama010/pyvista-js/commit/fdd5a3d4b46bc19852a6a25a41617ea6064d1b45))
- add Transifex link badge to README ([#283](https://github.com/tkoyama010/pyvista-js/issues/283)) ([3994ecc](https://github.com/tkoyama010/pyvista-js/commit/3994ecc6b8699318aa7c867e3d19a7c1e386a006))
- configure sphinxcontrib-typer to use HTML format with monokai theme ([#274](https://github.com/tkoyama010/pyvista-js/issues/274)) ([2aee477](https://github.com/tkoyama010/pyvista-js/commit/2aee477ac4313c65d97e84eee881a5974e09a307))
- expand typer usage HTML rendering to eliminate scrollbars ([#279](https://github.com/tkoyama010/pyvista-js/issues/279)) ([de3cff1](https://github.com/tkoyama010/pyvista-js/commit/de3cff1c66139e48ce2c88faab4aa1aa6b4b28bd))
- remove docs/locale/README.md ([#280](https://github.com/tkoyama010/pyvista-js/issues/280)) ([904a3c6](https://github.com/tkoyama010/pyvista-js/commit/904a3c65016c63ddc74e96850e6f33c9b76aecaa))
- replace Streamlit with stlite and add WASM explanation ([#263](https://github.com/tkoyama010/pyvista-js/issues/263)) ([b876898](https://github.com/tkoyama010/pyvista-js/commit/b876898663d4df05678e09596e84a5b5dfa24d55))
- update intro.py to install pyvista-js package directly ([#264](https://github.com/tkoyama010/pyvista-js/issues/264)) ([7d1c8c1](https://github.com/tkoyama010/pyvista-js/commit/7d1c8c1e6d85eddb1653aeeed98e49858d2f7346))

### Continuous Integration

- add nightly tests workflow per SPEC-0004 ([#271](https://github.com/tkoyama010/pyvista-js/issues/271)) ([974d531](https://github.com/tkoyama010/pyvista-js/commit/974d531a460462da731e2baacb2812d1be77bc94))
- add Renovate config for automated vtk.js version updates ([#273](https://github.com/tkoyama010/pyvista-js/issues/273)) ([3e1fcce](https://github.com/tkoyama010/pyvista-js/commit/3e1fccef43ecaa822d4a4728f362a8eb8c4260b8))

## [0.9.1](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.9.0...pyvista-js-v0.9.1) (2026-03-20)

### Bug Fixes

- add micropip jinja2 install to JupyterLite intro notebook ([#262](https://github.com/tkoyama010/pyvista-js/issues/262)) ([31ef65e](https://github.com/tkoyama010/pyvista-js/commit/31ef65e7dba04f74667a7f3d12b92dce022a08c3))
- rename simple_demo.py to intro.py in jupyterlite content ([#255](https://github.com/tkoyama010/pyvista-js/issues/255)) ([347cc54](https://github.com/tkoyama010/pyvista-js/commit/347cc54f577615cc93b7c71168d1920765f1205a))

## [0.9.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.8.0...pyvista-js-v0.9.0) (2026-03-20)

### Features

- Add lighting=None option to Plotter to disable default lights ([#241](https://github.com/tkoyama010/pyvista-js/issues/241)) ([4645d23](https://github.com/tkoyama010/pyvista-js/commit/4645d23164e3fb4c818d330f65dc587f95e9c428))
- add Plotter.add_scalar_bar() method for color legend display ([#175](https://github.com/tkoyama010/pyvista-js/issues/175)) ([4f8bbd2](https://github.com/tkoyama010/pyvista-js/commit/4f8bbd2d4f04143e85de93bac695b623cee43c6a))
- adopt SPEC 0 for minimum supported dependencies ([#248](https://github.com/tkoyama010/pyvista-js/issues/248)) ([33ab397](https://github.com/tkoyama010/pyvista-js/commit/33ab3976aa91f2997f62b5af70ab7bc52778c44b))

### Bug Fixes

- convert Light class color parameter lists to tuples consistently ([#238](https://github.com/tkoyama010/pyvista-js/issues/238)) ([dc1f5f3](https://github.com/tkoyama010/pyvista-js/commit/dc1f5f311f4639131e1869cbfd807403a917b7c0))
- restrict atsphinx-stlite to python < 3.14 in docs extras ([#258](https://github.com/tkoyama010/pyvista-js/issues/258)) ([d8542ab](https://github.com/tkoyama010/pyvista-js/commit/d8542ab7d804ee6e0feb0ac6a792c7ef55be1d92))
- restrict jupyterlite packages to python < 3.14 in docs extras ([#259](https://github.com/tkoyama010/pyvista-js/issues/259)) ([dbcf1c5](https://github.com/tkoyama010/pyvista-js/commit/dbcf1c5a0e9aa346e654254bfaf9194a97d1f063))
- restrict remaining pinned docs deps to python < 3.14 ([#260](https://github.com/tkoyama010/pyvista-js/issues/260)) ([34e40be](https://github.com/tkoyama010/pyvista-js/commit/34e40be5917e223169615a7b234fc9b5d5b7a928))

### Documentation

- add CLI reference documentation ([#242](https://github.com/tkoyama010/pyvista-js/issues/242)) ([ef31faf](https://github.com/tkoyama010/pyvista-js/commit/ef31faff2b6a595b776fe6e8291ced6822c51af8))

### Continuous Integration

- add uv-lock-check hook to pre-commit config ([#251](https://github.com/tkoyama010/pyvista-js/issues/251)) ([1e56ed4](https://github.com/tkoyama010/pyvista-js/commit/1e56ed42b43164b7b3df1eabe14bebddacbe3ac5))

## [0.8.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.7.1...pyvista-js-v0.8.0) (2026-03-19)

### Features

- add --load-pickle option to plot command for loading pickled Plotter objects ([#233](https://github.com/tkoyama010/pyvista-js/issues/233)) ([31bdfcb](https://github.com/tkoyama010/pyvista-js/commit/31bdfcb8d04b7a376648a746dfc2fb8784907a93))
- add --pickle option to plot command for saving Plotter objects ([#231](https://github.com/tkoyama010/pyvista-js/issues/231)) ([a2c3ed5](https://github.com/tkoyama010/pyvista-js/commit/a2c3ed552b108441b99841a9fb278f642c07a5a0))
- add enable_parallel_projection support ([#222](https://github.com/tkoyama010/pyvista-js/issues/222)) ([c8d6d93](https://github.com/tkoyama010/pyvista-js/commit/c8d6d9396bbd1e075d4c9a6dda6a0ebea57e19bc))
- add Stanford Bunny example function ([#221](https://github.com/tkoyama010/pyvista-js/issues/221)) ([b800a88](https://github.com/tkoyama010/pyvista-js/commit/b800a88a5dfef6f30f14998675d1777c7d590923))
- update capture-preview CLI to use Stanford Bunny with Playwright mouse drag rotation ([#227](https://github.com/tkoyama010/pyvista-js/issues/227)) ([632f3e1](https://github.com/tkoyama010/pyvista-js/commit/632f3e1311a6765861e8dc03ad90d53d5ef93c68))

## [0.7.1](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.7.0...pyvista-js-v0.7.1) (2026-03-18)

### Continuous Integration

- add token parameter to Codecov action for authentication ([#217](https://github.com/tkoyama010/pyvista-js/issues/217)) ([0f33f44](https://github.com/tkoyama010/pyvista-js/commit/0f33f44094fb90da5cf7148f197c61fe08d1245f))

## [0.7.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.6.0...pyvista-js-v0.7.0) (2026-03-18)

### Features

- add clip filter to PolyData ([#165](https://github.com/tkoyama010/pyvista-js/issues/165)) ([887b78b](https://github.com/tkoyama010/pyvista-js/commit/887b78bed1b972a7a2b37d9765565301c12eddcb))
- Add Codecov integration for code coverage reporting ([#208](https://github.com/tkoyama010/pyvista-js/issues/208)) ([da0ba52](https://github.com/tkoyama010/pyvista-js/commit/da0ba522188d1adac0b220fd3f9a7b6daf717bbd))
- Add Plotter.add_axes() orientation marker widget ([#214](https://github.com/tkoyama010/pyvista-js/issues/214)) ([dd75c89](https://github.com/tkoyama010/pyvista-js/commit/dd75c8998c98836059c0f3c522a3d20a93d3fdea))
- add Zenodo integration for DOI citation ([#209](https://github.com/tkoyama010/pyvista-js/issues/209)) ([2edb753](https://github.com/tkoyama010/pyvista-js/commit/2edb753e2f99d9631e7b0913055dda8b8fbba626))

## [0.6.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.5.1...pyvista-js-v0.6.0) (2026-03-18)

### Features

- add cpos parameter to show() method matching PyVista's camera positioning interface ([#204](https://github.com/tkoyama010/pyvista-js/issues/204)) ([d3dc702](https://github.com/tkoyama010/pyvista-js/commit/d3dc70263f9dd47d387b1082ef8933ec2a2f0d7c))
- add STL file reader ([#168](https://github.com/tkoyama010/pyvista-js/issues/168)) ([cb43ae8](https://github.com/tkoyama010/pyvista-js/commit/cb43ae8318fff83ba8d159f582fded6f94de315c))
- Migrate CLI from argparse to Typer ([#196](https://github.com/tkoyama010/pyvista-js/issues/196)) ([db23b8a](https://github.com/tkoyama010/pyvista-js/commit/db23b8ae8c49793a86c1fd404ca63c846a8d02b5))

### Documentation

- add `{include} ../README.md` to docs/index.md ([#201](https://github.com/tkoyama010/pyvista-js/issues/201)) ([04345f5](https://github.com/tkoyama010/pyvista-js/commit/04345f5711338e308ded41c508ece1faf0f419a9))

## [0.5.1](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.5.0...pyvista-js-v0.5.1) (2026-03-18)

### Bug Fixes

- use absolute GitHub URL for preview.gif to render on PyPI ([#192](https://github.com/tkoyama010/pyvista-js/issues/192)) ([b679882](https://github.com/tkoyama010/pyvista-js/commit/b6798821c4d6318585a979fb0ff68ab99d5c6fb4))

## [0.5.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.4.0...pyvista-js-v0.5.0) (2026-03-17)

### Features

- add edge and wireframe rendering options to add_mesh ([#173](https://github.com/tkoyama010/pyvista-js/issues/173)) ([930f476](https://github.com/tkoyama010/pyvista-js/commit/930f476419aa803ead2d6f0ddce58143190a9be9))
- add PointData class with scalar array support and colormap rendering ([#190](https://github.com/tkoyama010/pyvista-js/issues/190)) ([b43d7f3](https://github.com/tkoyama010/pyvista-js/commit/b43d7f3c6f7acf117b320d819631d61f48ec2ca3))
- add preview image to README with automated capture script ([#180](https://github.com/tkoyama010/pyvista-js/issues/180)) ([4957d0a](https://github.com/tkoyama010/pyvista-js/commit/4957d0a88d0721f5687d5e1e3ae854e04980048b))
- add standard camera view methods to Plotter ([#171](https://github.com/tkoyama010/pyvista-js/issues/171)) ([bc2e53e](https://github.com/tkoyama010/pyvista-js/commit/bc2e53ec520ba4db31f29da71e004c717be5a7ff))
- add tube filter to PolyData ([#166](https://github.com/tkoyama010/pyvista-js/issues/166)) ([01145e8](https://github.com/tkoyama010/pyvista-js/commit/01145e89fc3f1672dbcbf75f12f4613fbed5acbc))

### Bug Fixes

- enable persist-credentials for git-auto-commit-action ([#182](https://github.com/tkoyama010/pyvista-js/issues/182)) ([8166602](https://github.com/tkoyama010/pyvista-js/commit/8166602544be46250ce8a9cf9c5543e0dbb9a7e9))
- install pyvista-js package in update-preview workflow ([#181](https://github.com/tkoyama010/pyvista-js/issues/181)) ([2047a96](https://github.com/tkoyama010/pyvista-js/commit/2047a96ec7945faac69e5bd780c2302a4797345a))
- match Cube point generation to vtk.js vtkCubeSource (24 points per mesh) ([#187](https://github.com/tkoyama010/pyvista-js/issues/187)) ([54db900](https://github.com/tkoyama010/pyvista-js/commit/54db9007817ff7f3f63272465e8be0d73770de5c))
- match Cylinder point generation to vtk.js vtkCylinderSource ordering ([#188](https://github.com/tkoyama010/pyvista-js/issues/188)) ([e4679bf](https://github.com/tkoyama010/pyvista-js/commit/e4679bfbaa79f11cfa160df3a62f85887a05b332))
- match Disc/Circle point generation to vtk.js vtkDiskSource ordering ([#189](https://github.com/tkoyama010/pyvista-js/issues/189)) ([154484f](https://github.com/tkoyama010/pyvista-js/commit/154484f3fc6de8288db500e31dd643b993e9fcd4))
- match Sphere point generation to vtk.js vtkSphereSource ordering ([#186](https://github.com/tkoyama010/pyvista-js/issues/186)) ([18180df](https://github.com/tkoyama010/pyvista-js/commit/18180dfa5b577bffd1b74eaa2acd66146a43dfa1))
- use double-click to open notebook in JupyterLite ([#183](https://github.com/tkoyama010/pyvista-js/issues/183)) ([4c81ce4](https://github.com/tkoyama010/pyvista-js/commit/4c81ce4b11d9b298a949d80438df27f51803034e))

### Documentation

- center "Try it in your browser" link in README ([#184](https://github.com/tkoyama010/pyvista-js/issues/184)) ([66f9b4f](https://github.com/tkoyama010/pyvista-js/commit/66f9b4f325389ba5197132c064b7446c2ae634b4))

## [0.4.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.3.0...pyvista-js-v0.4.0) (2026-03-16)

### Features

- add Cone geometric primitive ([#157](https://github.com/tkoyama010/pyvista-js/issues/157)) ([7425084](https://github.com/tkoyama010/pyvista-js/commit/742508477217f4fe22b1c3e43f0cd45973411356))
- add Disc geometric primitive ([#158](https://github.com/tkoyama010/pyvista-js/issues/158)) ([268f9e6](https://github.com/tkoyama010/pyvista-js/commit/268f9e680945be070505be62e0850905cb048193))
- Add Line geometric primitive ([#159](https://github.com/tkoyama010/pyvista-js/issues/159)) ([9381a10](https://github.com/tkoyama010/pyvista-js/commit/9381a10b7a8355f43a4c55fb38fd7607a1c350c7))
- add Plane geometric primitive ([#156](https://github.com/tkoyama010/pyvista-js/issues/156)) ([e8870bc](https://github.com/tkoyama010/pyvista-js/commit/e8870bca2b091fbee7d37046eeb86bb473499ed4))

### Continuous Integration

- add Conventional Commits PR title check ([#162](https://github.com/tkoyama010/pyvista-js/issues/162)) ([ec91fc6](https://github.com/tkoyama010/pyvista-js/commit/ec91fc65062791b136bd40b48bf6adebb36b82f1))

## [0.3.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.2.3...pyvista-js-v0.3.0) (2026-03-15)

### Features

- add Circle primitive mirroring pyvista.Circle API ([#138](https://github.com/tkoyama010/pyvista-js/issues/138)) ([555903d](https://github.com/tkoyama010/pyvista-js/commit/555903dfebb5d3b9b6088c42b72249accb4a3798))
- add CLI with plot and info subcommands ([#135](https://github.com/tkoyama010/pyvista-js/issues/135)) ([86245b7](https://github.com/tkoyama010/pyvista-js/commit/86245b7dc6921f7dffa646dd234a1597475d1012))
- add PolyData.save() using meshio and examples.download_trumpet() ([#139](https://github.com/tkoyama010/pyvista-js/issues/139)) ([2804ece](https://github.com/tkoyama010/pyvista-js/commit/2804ece0475f7507f5561a9660d1ea793c7e1cd5))
- add shrink filter to PolyData ([#132](https://github.com/tkoyama010/pyvista-js/issues/132)) ([84de11b](https://github.com/tkoyama010/pyvista-js/commit/84de11b0b5275057e565bd37a0fa028d3c191aec))
- add Texture class and texture mapping support ([#136](https://github.com/tkoyama010/pyvista-js/issues/136)) ([1659914](https://github.com/tkoyama010/pyvista-js/commit/16599146b3f2093e2aff6af5c427beebafdc39ea))

### Documentation

- add claude as a contributor for code ([#134](https://github.com/tkoyama010/pyvista-js/issues/134)) ([74a63d0](https://github.com/tkoyama010/pyvista-js/commit/74a63d009cca827678880f1869ee4e6e666c08f2))

## [0.2.3](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.2.2...pyvista-js-v0.2.3) (2026-03-14)

### Continuous Integration

- fix PyPI Trusted Publishing failure caused by reusable workflow ([#130](https://github.com/tkoyama010/pyvista-js/issues/130)) ([c94ca18](https://github.com/tkoyama010/pyvista-js/commit/c94ca185395c3f903387e2cb743a6328705d12fc))

## [0.2.2](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.2.1...pyvista-js-v0.2.2) (2026-03-14)

### Features

- add Camera class with PyVista-like API ([#123](https://github.com/tkoyama010/pyvista-js/issues/123)) ([0a06d71](https://github.com/tkoyama010/pyvista-js/commit/0a06d715a541ab9ad2c88dbab6b104b8d4097409))
- add Light class for scene lighting control ([#122](https://github.com/tkoyama010/pyvista-js/issues/122)) ([9fd6f3e](https://github.com/tkoyama010/pyvista-js/commit/9fd6f3ef75281f51906124160719f2d26afe4b91))
- add PolyData class and deprecate Mesh ([#121](https://github.com/tkoyama010/pyvista-js/issues/121)) ([92cd85c](https://github.com/tkoyama010/pyvista-js/commit/92cd85c0f84cf5069a0557690228cf2171fe4389))
- add plot method to Mesh class ([#118](https://github.com/tkoyama010/pyvista-js/issues/118)) ([1f42f54](https://github.com/tkoyama010/pyvista-js/commit/1f42f54ceb49aaffbbc0a4cdd76aa2449af4868c))
- add zizmor pre-commit hook and badge ([#115](https://github.com/tkoyama010/pyvista-js/issues/115)) ([862cb75](https://github.com/tkoyama010/pyvista-js/commit/862cb75894c4e5cf836f17ee1e1e1595af7f2b30))
- add OBJReader for Wavefront OBJ files ([#112](https://github.com/tkoyama010/pyvista-js/issues/112)) ([567e06c](https://github.com/tkoyama010/pyvista-js/commit/567e06ce0ffbba46b6fc6a51ed678b1a7e909388))
- add PLYReader for ASCII PLY files ([#111](https://github.com/tkoyama010/pyvista-js/issues/111)) ([a4e06b9](https://github.com/tkoyama010/pyvista-js/commit/a4e06b9934ae91752324d19422a96c6a6936e6fc))
- add PolyDataReader for legacy VTK files ([#108](https://github.com/tkoyama010/pyvista-js/issues/108)) ([813e702](https://github.com/tkoyama010/pyvista-js/commit/813e70258fb5266b4c1829138b0b403d2a5a1698))
- add Mesh.bounding_sphere property ([#100](https://github.com/tkoyama010/pyvista-js/issues/100)) ([b673a46](https://github.com/tkoyama010/pyvista-js/commit/b673a4666be8f80fc080bb4ee5c89dce84b4678c))
- open default browser full-screen when running Python ([#98](https://github.com/tkoyama010/pyvista-js/issues/98)) ([9932c60](https://github.com/tkoyama010/pyvista-js/commit/9932c607401de23dd7684e9a01ecf527620a2fec))

### Bug Fixes

- grant `contents: read` to the `publish` reusable workflow call ([#126](https://github.com/tkoyama010/pyvista-js/issues/126)) ([4fe156e](https://github.com/tkoyama010/pyvista-js/commit/4fe156e0aa4d907bbb2974bae82e98e136d75cd6))
- update bootstrap-sha to correct commit ([#125](https://github.com/tkoyama010/pyvista-js/issues/125)) ([87618e5](https://github.com/tkoyama010/pyvista-js/commit/87618e5bfd7ba724fe04482f4e67533e99f3ec5a))
- remove duplicate js directory from wheel build ([#92](https://github.com/tkoyama010/pyvista-js/issues/92)) ([dcc7859](https://github.com/tkoyama010/pyvista-js/commit/dcc78599b7faa13454cdd1cb6948db3c8fcce685))

### Documentation

- add Diátaxis badge to README ([#120](https://github.com/tkoyama010/pyvista-js/issues/120)) ([638bc26](https://github.com/tkoyama010/pyvista-js/commit/638bc263f22533e2f702f37933034ce995d011f6))
- add Diátaxis landing page with card-based navigation ([#119](https://github.com/tkoyama010/pyvista-js/issues/119)) ([720e5d5](https://github.com/tkoyama010/pyvista-js/commit/720e5d599da4de1c38216a3bb9a864a23ac308c2))
- add GitHub Discussions badge to README ([#117](https://github.com/tkoyama010/pyvista-js/issues/117)) ([88a181b](https://github.com/tkoyama010/pyvista-js/commit/88a181b584a7785ebbeea5695c9eb4577969edc6))
- add claude as a contributor for maintenance ([#116](https://github.com/tkoyama010/pyvista-js/issues/116)) ([6319673](https://github.com/tkoyama010/pyvista-js/commit/6319673841253779594bca81623ee81073afa320))
- add SECURITY.md ([#114](https://github.com/tkoyama010/pyvista-js/issues/114)) ([4e31038](https://github.com/tkoyama010/pyvista-js/commit/4e3103894eebcc6b45141911d6f52a0ba67be833))
- add atsphinx-stlite for interactive Streamlit demo ([#107](https://github.com/tkoyama010/pyvista-js/issues/107)) ([ffde3e3](https://github.com/tkoyama010/pyvista-js/commit/ffde3e32e63b298b78fe17d54bc0d9ce9087ad9e))
- enable global_enable_try_examples for interactive docstring examples ([#106](https://github.com/tkoyama010/pyvista-js/issues/106)) ([f3e68ca](https://github.com/tkoyama010/pyvista-js/commit/f3e68ca8d3056e7e8953b1caa6808409e31ca4e4))
- add CITATION.cff ([#110](https://github.com/tkoyama010/pyvista-js/issues/110)) ([a72d032](https://github.com/tkoyama010/pyvista-js/commit/a72d032bafd592fa203f04bcba0ab2c7af018ee5))
- add API reference documentation ([#105](https://github.com/tkoyama010/pyvista-js/issues/105)) ([81345f5](https://github.com/tkoyama010/pyvista-js/commit/81345f5e3b03a9ed89e2cd4b83aa47a94b934836))
- update Code of Conduct with reporting contact and remove placeholder note ([#102](https://github.com/tkoyama010/pyvista-js/issues/102)) ([bc249cc](https://github.com/tkoyama010/pyvista-js/commit/bc249ccdea726e7a8c41512a672e1bb940b58645))
- add Code of Conduct badge to README ([#101](https://github.com/tkoyama010/pyvista-js/issues/101)) ([11c742c](https://github.com/tkoyama010/pyvista-js/commit/11c742cdc86627d5693269e589161df5f46825d5))
- add star history chart to Contributing section ([#99](https://github.com/tkoyama010/pyvista-js/issues/99)) ([7e22160](https://github.com/tkoyama010/pyvista-js/commit/7e22160e350cf52f54261a8072e2fd4df76349d6))
- add ✨ Try it in your browser ✨ link ([#97](https://github.com/tkoyama010/pyvista-js/issues/97)) ([cbfad58](https://github.com/tkoyama010/pyvista-js/commit/cbfad58f58b7ed20a072fbda0b851bf0f131c351))
- add dependabot as a contributor for maintenance ([#96](https://github.com/tkoyama010/pyvista-js/issues/96)) ([385dace](https://github.com/tkoyama010/pyvista-js/commit/385dace5c84ed79a0d25c1dfadf592b19ca87b1a))
- update README to follow standard-readme spec ([#93](https://github.com/tkoyama010/pyvista-js/issues/93)) ([11afce5](https://github.com/tkoyama010/pyvista-js/commit/11afce5f7a79bcf8c19110f06fd3d936300f4f57))

### Continuous Integration

- add release-please automation ([#124](https://github.com/tkoyama010/pyvista-js/issues/124)) ([eabc55a](https://github.com/tkoyama010/pyvista-js/commit/eabc55a252c39f3a8d3670ed878ffdcdeeddf1cb))
- replace local standard-readme hook with remote pre-commit repo ([#103](https://github.com/tkoyama010/pyvista-js/issues/103)) ([2f59a9f](https://github.com/tkoyama010/pyvista-js/commit/2f59a9fe4b16b8cd2c1ff1ee5e9a535eda092b4f))
