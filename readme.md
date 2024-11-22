# gitm (git monorepo)

gitm is a minimalist monorepo for git using libgit2.

## Getting Started

### Installing

gitm only works on linux and other unix-like operating systems (for now).

```
git clone git@github.com:michae107/gitm.git
cd gitm
./install
```

### Usage

To create a new monorepo simply run `gitm init` in the desired directory, this will create the `.gitm` file (you can refer to the [.gitm in the tests directory](./tests/.gitm) for an example). Add any repositories you want in the same format as .gitmodules:

```
[submodule "TheAlgorithms/C"]
    path = algorithms
    url = https://github.com/TheAlgorithms/C
```

Run `gitm update` to clone your new submodule (and any git submodules it has) and recursively initialise any `.gitm` files in those submodules.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

