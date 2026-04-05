[![GitHub license](https://img.shields.io/github/license/openmv/openmv-datasheets?label=license%20%E2%9A%96)](https://github.com/openmv/openmv-datasheets/blob/master/LICENSE)
[![GitHub forks](https://img.shields.io/github/forks/openmv/openmv-datasheets?color=green)](https://github.com/openmv/openmv-datasheets/network)
[![GitHub stars](https://img.shields.io/github/stars/openmv/openmv-datasheets?color=yellow)](https://github.com/openmv/openmv-datasheets/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/openmv/openmv-datasheets?color=orange)](https://github.com/openmv/openmv-datasheets/issues)

<img width="480" src="https://raw.githubusercontent.com/openmv/openmv-media/master/logos/openmv-logo/logo.png">

# OpenMV Datasheets

Auto-generated PDF datasheets for all [OpenMV](https://openmv.io) products — cameras, shields, sensors, lenses, and accessories.

- [Building](#building)
- [Product Categories](#product-categories)
- [Contributing to the project](#contributing-to-the-project)
  + [Contribution guidelines](#contribution-guidelines)

---

## Building

```bash
pip install -r requirements.txt
python build.py              # Build all datasheets
python build.py openmv-cam-h7  # Build a specific product
python build.py --list       # List available products
```

Output PDFs are written to `output/` organized by category:

```
output/
  cameras/       # OpenMV Cam boards
  shields/       # Expansion shields
  sensors/       # Camera modules
  lenses/        # M8 and M12 lenses
  accessories/   # Cases, cables, filters, breakouts
```

---

## Product Categories

| Category | Count | Description |
|----------|-------|-------------|
| [Cameras](products/cameras/) | 10 | OpenMV Cam boards (M4, M7, H7, RT1062, AE3, N6, Pure Thermal) |
| [Shields](products/shields/) | 22 | Expansion shields (servo, motor, PoE, CAN, relay, LCD, WiFi, etc.) |
| [Sensors](products/sensors/) | 8 | Camera modules (OV5640, FLIR, GENX320, global shutter, etc.) |
| [Lenses](products/lenses/) | 8 | M8 and M12 lenses (wide angle, telephoto, fish eye, IR) |
| [Accessories](products/accessories/) | 7 | Cases, cables, filters, lens mounts, breakouts |

---

## Contributing to the project

Contributions are most welcome. If you are interested in contributing to the project, start by creating a fork of the following repository:

* https://github.com/openmv/openmv-datasheets.git

Clone the forked repository, and add a remote to the main repository:
```bash
git clone --recursive https://github.com/<username>/openmv-datasheets.git
git -C openmv-datasheets remote add upstream https://github.com/openmv/openmv-datasheets.git
```

Now the repository is ready for pull requests. To send a pull request, create a new feature branch and push it to origin, and use GitHub to create the pull request from the forked repository to the upstream openmv/openmv-datasheets repository. For example:
```bash
git checkout -b <some_branch_name>
<commit changes>
git push origin -u <some_branch_name>
```

### Contribution guidelines

Please follow the [best practices](https://developers.google.com/blockly/guides/modify/contribute/write_a_good_pr) when sending pull requests upstream. In general, the pull request should:
* Fix one problem. Don't try to tackle multiple issues at once.
* Split the changes into logical groups using git commits.
* Pull request title should be less than 78 characters, and match this pattern:
  * `<scope>:<1 space><description><.>`
* Commit subject line should be less than 78 characters, and match this pattern:
  * `<scope>:<1 space><description><.>`
