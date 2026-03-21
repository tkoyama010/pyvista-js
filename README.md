# pyvista-js

[![PyPI](https://img.shields.io/pypi/v/pyvista-js.svg)](https://pypi.org/project/pyvista-js/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19092335.svg)](https://doi.org/10.5281/zenodo.19092335)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![SPEC 0 — Minimum Supported Dependencies](https://img.shields.io/badge/SPEC-0-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0000/)
[![SPEC 6 — Upper Bound Constraints on Dependencies](https://img.shields.io/badge/SPEC-6-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0006/)
[![SPEC 7 — Seeding Pseudo-Random Number Generation](https://img.shields.io/badge/SPEC-7-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0007/)
[![codecov](https://codecov.io/gh/tkoyama010/pyvista-js/branch/main/graph/badge.svg)](https://codecov.io/gh/tkoyama010/pyvista-js)
[![Documentation Status](https://readthedocs.org/projects/pyvista-js/badge/?version=latest)](https://pyvista-js.readthedocs.io/en/latest/?badge=latest)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/tkoyama010/pyvista-js/main.svg)](https://results.pre-commit.ci/latest/github/tkoyama010/pyvista-js/main)
[![JupyterLite](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://tkoyama010.github.io/pyvista-js/)
![All Contributors](https://img.shields.io/github/all-contributors/tkoyama010/pyvista-js?color=ee8449)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-3.0-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)
[![djlint](https://img.shields.io/badge/html%20templates-djLint-blueviolet.svg)](https://www.djlint.com)
[![zizmor](https://img.shields.io/badge/%F0%9F%8C%88-zizmor-white?labelColor=white)](https://zizmor.sh/)
[![Diátaxis](https://img.shields.io/badge/Documentation-Di%C3%A1taxis-blue.svg?style=flat)](https://diataxis.fr/)
[![Join the community](https://img.shields.io/badge/Join%20the%20community-on%20GitHub%20Discussions-blue)](https://github.com/tkoyama010/pyvista-js/discussions)

[PyVista](https://github.com/pyvista/pyvista)-like API for [vtk.js](https://github.com/Kitware/vtk-js) — bring intuitive 3D visualization to the browser.

<p align="center">✨ <strong><a href="https://tkoyama010.github.io/pyvista-js/">Try it in your browser</a></strong> ✨</p>

![pyvista-js rendering in JupyterLite](https://raw.githubusercontent.com/tkoyama010/pyvista-js/main/assets/preview.gif)

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [Citation](#citation)
- [Contributing](#contributing)
- [License](#license)

## Install

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
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tkoyama010"><img src="https://avatars.githubusercontent.com/u/7513610?v=4?s=100" width="100px;" alt="Tetsuo Koyama"/><br /><sub><b>Tetsuo Koyama</b></sub></a><br /><a href="#ideas-tkoyama010" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/tkoyama010/pyvista-js/commits?author=tkoyama010" title="Documentation">📖</a> <a href="https://github.com/tkoyama010/pyvista-js/commits?author=tkoyama010" title="Code">💻</a> <a href="https://github.com/tkoyama010/pyvista-js/pulls?q=is%3Apr+reviewed-by%3Atkoyama010" title="Reviewed Pull Requests">👀</a> <a href="https://github.com/tkoyama010/pyvista-js/issues?q=author%3Atkoyama010" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://allcontributors.org"><img src="https://avatars.githubusercontent.com/u/46410174?v=4?s=100" width="100px;" alt="All Contributors"/><br /><sub><b>All Contributors</b></sub></a><br /><a href="https://github.com/tkoyama010/pyvista-js/commits?author=all-contributors" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://pre-commit.com"><img src="https://avatars.githubusercontent.com/u/6943086?v=4?s=100" width="100px;" alt="pre-commit"/><br /><sub><b>pre-commit</b></sub></a><br /><a href="#maintenance-pre-commit" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://anthropic.com/claude-code"><img src="https://avatars.githubusercontent.com/u/81847?v=4?s=100" width="100px;" alt="Claude"/><br /><sub><b>Claude</b></sub></a><br /><a href="https://github.com/tkoyama010/pyvista-js/issues?q=author%3Aclaude" title="Bug reports">🐛</a> <a href="#maintenance-claude" title="Maintenance">🚧</a> <a href="https://github.com/tkoyama010/pyvista-js/commits?author=claude" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/features/security"><img src="https://avatars.githubusercontent.com/u/27347476?v=4?s=100" width="100px;" alt="Dependabot"/><br /><sub><b>Dependabot</b></sub></a><br /><a href="#maintenance-dependabot" title="Maintenance">🚧</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->

<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## License

[BSD 3-Clause](LICENSE) © Tetsuo Koyama
