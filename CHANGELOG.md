# Changelog

## [0.7.0](https://github.com/tkoyama010/pyvista-js/compare/pyvista-js-v0.6.0...pyvista-js-v0.7.0) (2026-03-18)


### Features

* add clip filter to PolyData ([#165](https://github.com/tkoyama010/pyvista-js/issues/165)) ([887b78b](https://github.com/tkoyama010/pyvista-js/commit/887b78bed1b972a7a2b37d9765565301c12eddcb))
* Add Codecov integration for code coverage reporting ([#208](https://github.com/tkoyama010/pyvista-js/issues/208)) ([da0ba52](https://github.com/tkoyama010/pyvista-js/commit/da0ba522188d1adac0b220fd3f9a7b6daf717bbd))
* Add Plotter.add_axes() orientation marker widget ([#214](https://github.com/tkoyama010/pyvista-js/issues/214)) ([dd75c89](https://github.com/tkoyama010/pyvista-js/commit/dd75c8998c98836059c0f3c522a3d20a93d3fdea))
* add Zenodo integration for DOI citation ([#209](https://github.com/tkoyama010/pyvista-js/issues/209)) ([2edb753](https://github.com/tkoyama010/pyvista-js/commit/2edb753e2f99d9631e7b0913055dda8b8fbba626))

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
