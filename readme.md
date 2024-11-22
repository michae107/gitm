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

To create a new monorepo simply run `gitm init` in the desired directory, this will create an empty `.gitm` file and initialise a new git repository for it. Add any repositories you want into the .gitm file using the same format as .gitmodules (refer to the [.gitm in the tests directory](./tests/.gitm) for another example):

```
[submodule "TheAlgorithms/C"]
    path = algorithms
    url = https://github.com/TheAlgorithms/C
```

Run `gitm update` to clone your new submodule (and any git submodules it has) and recursively initialise any `.gitm` files in those submodules.

After that commit your changes to the .gitm file:

```
git add .
git commit -m "init gitm repository"
```

You now have a git repository containing all the submodules listed in your .gitm file that you can publish where you publish other git repositories.

## Features needed

- deleting submodules with the command-line
- a way to view the status of subrepositories
- other useful features that a simple monorepo might want

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

