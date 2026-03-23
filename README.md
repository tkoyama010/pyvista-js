# pyvista-js

[![Documentation Status](https://readthedocs.org/projects/pyvista-js/badge/?version=latest)](https://pyvista-js.readthedocs.io/en/latest/?badge=latest)
[![JupyterLite](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://tkoyama010.github.io/pyvista-js/)
[![stlite](https://img.shields.io/badge/stlite-lite_now-FF4B4B?logo=streamlit&logoColor=white)](https://tkoyama010.github.io/pyvista-js/stlite)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme)

[PyVista](https://github.com/pyvista/pyvista)-like API for [vtk.js](https://github.com/Kitware/vtk-js) — bring intuitive 3D visualization to the browser.

| [Try it with JupyterLite] | [Try it with Stlite] |
| :-----------------------: | :------------------: |
| ![jupyterlite-preview] | ![stlite-preview] |

## Table of Contents

<!-- mdformat-toc start --slug=github --no-anchors --maxlevel=6 --minlevel=2 -->

- [Table of Contents](#table-of-contents)
- [Install](#install)
- [Usage](#usage)
- [Citation](#citation)
- [Contributing](#contributing)
- [License](#license)

<!-- mdformat-toc end -->

## Install

[![PyPI](https://img.shields.io/pypi/v/pyvista-js.svg)](https://pypi.org/project/pyvista-js/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

```bash
pip install pyvista-js
```

For Pyodide/stlite:

```python
import micropip

await micropip.install("pyvista-js")
```

## Usage

```python
import pyvista_js as pv

plotter = pv.Plotter()
plotter.add_mesh(pv.Sphere(), color="red")
plotter.show()
```

## Citation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19092335.svg)](https://doi.org/10.5281/zenodo.19092335)

If you use pyvista-js in your research or projects, please cite it using the following:

```bibtex
@software{koyama_pyvista_js,
  author       = {Koyama, Tetsuo},
  title        = {pyvista-js: A PyVista-like API for 3D visualization in the browser},
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19092335},
  url          = {https://github.com/tkoyama010/pyvista-js}
}
```

Alternatively, you can use the [CITATION.cff](CITATION.cff) file in this repository, which follows the [Citation File Format](https://citation-file-format.github.io/) standard.

## Contributing

![All Contributors](https://img.shields.io/github/all-contributors/tkoyama010/pyvista-js?color=ee8449)

Enjoying pyvista-js? Show your support with a GitHub star — it's a simple click that means the world to us and helps others discover it, too!

<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=tkoyama010/pyvista-js&type=Date">
  <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=tkoyama010/pyvista-js&type=Date&theme=dark">
  <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=tkoyama010/pyvista-js&type=Date">
</picture>

Contributions are welcome! Please open an issue or pull request on [GitHub](https://github.com/tkoyama010/pyvista-js/issues).

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tkoyama010"><img src="https://avatars.githubusercontent.com/u/7513610?v=4?s=100" width="100px;" alt="Tetsuo Koyama"/><br /><sub><b>Tetsuo Koyama</b></sub></a><br /><a href="#ideas-tkoyama010" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/tkoyama010/pyvista-js/commits?author=tkoyama010" title="Documentation">📖</a> <a href="https://github.com/tkoyama010/pyvista-js/commits?author=tkoyama010" title="Code">💻</a> <a href="https://github.com/tkoyama010/pyvista-js/pulls?q=is%3Apr+reviewed-by%3Atkoyama010" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/tkoyama010/pyvista-js/issues?q=author%3Atkoyama010" title="Bug reports">🐛</a> <a href="#translation-tkoyama010" title="Translation">🌍</a> <a href="#platform-tkoyama010" title="Packaging/porting to new platform">📦</a> <a href="#projectManagement-tkoyama010" title="Project Management">📆</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://allcontributors.org"><img src="https://avatars.githubusercontent.com/u/46410174?v=4?s=100" width="100px;" alt="All Contributors"/><br /><sub><b>All Contributors</b></sub></a><br /><a href="https://github.com/tkoyama010/pyvista-js/commits?author=all-contributors" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://pre-commit.com"><img src="https://avatars.githubusercontent.com/u/6943086?v=4?s=100" width="100px;" alt="pre-commit"/><br /><sub><b>pre-commit</b></sub></a><br /><a href="#maintenance-pre-commit" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://anthropic.com/claude-code"><img src="https://avatars.githubusercontent.com/u/81847?v=4?s=100" width="100px;" alt="Claude"/><br /><sub><b>Claude</b></sub></a><br /><a href="https://github.com/tkoyama010/pyvista-js/issues?q=author%3Aclaude" title="Bug reports">🐛</a> <a href="#maintenance-claude" title="Maintenance">🚧</a> <a href="https://github.com/tkoyama010/pyvista-js/commits?author=claude" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/features/security"><img src="https://avatars.githubusercontent.com/u/27347476?v=4?s=100" width="100px;" alt="Dependabot"/><br /><sub><b>Dependabot</b></sub></a><br /><a href="#maintenance-dependabot" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.transifex.com/"><img src="https://avatars.githubusercontent.com/u/22542?v=4?s=100" width="100px;" alt="Transifex"/><br /><sub><b>Transifex</b></sub></a><br /><a href="https://github.com/tkoyama010/pyvista-js/commits?author=transifex" title="Documentation">📖</a> <a href="#translation-transifex" title="Translation">🌍</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## License

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

[BSD 3-Clause](LICENSE) © Tetsuo Koyama

[jupyterlite-preview]: https://raw.githubusercontent.com/tkoyama010/pyvista-js/main/assets/preview.gif
[stlite-preview]: https://raw.githubusercontent.com/tkoyama010/pyvista-js/main/assets/stlite-preview.gif
[try it with jupyterlite]: https://tkoyama010.github.io/pyvista-js/
[try it with stlite]: https://tkoyama010.github.io/pyvista-js/stlite
