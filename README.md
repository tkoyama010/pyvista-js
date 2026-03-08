# pyvista-js

[![PyPI](https://img.shields.io/pypi/v/pyvista-js.svg)](https://pypi.org/project/pyvista-js/)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Documentation Status](https://readthedocs.org/projects/pyvista-js/badge/?version=latest)](https://pyvista-js.readthedocs.io/en/latest/?badge=latest)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/tkoyama010/pyvista-js/main.svg)](https://results.pre-commit.ci/latest/github/tkoyama010/pyvista-js/main)
[![JupyterLite](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://tkoyama010.github.io/pyvista-js/)
![All Contributors](https://img.shields.io/github/all-contributors/tkoyama010/pyvista-js?color=ee8449)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme)

[PyVista](https://github.com/pyvista/pyvista)-like API for [vtk.js](https://github.com/Kitware/vtk-js) — bring intuitive 3D visualization to the browser.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
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

## Contributing

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
      <td align="center" valign="top" width="14.28%"><a href="https://anthropic.com/claude-code"><img src="https://avatars.githubusercontent.com/u/81847?v=4?s=100" width="100px;" alt="Claude"/><br /><sub><b>Claude</b></sub></a><br /><a href="https://github.com/tkoyama010/pyvista-js/issues?q=author%3Aclaude" title="Bug reports">🐛</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->

<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## License

[BSD 3-Clause](LICENSE) © Tetsuo Koyama
