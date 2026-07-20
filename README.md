# Pac-man

## Conception

This branch is made not to share history with the code-dedicated branches. It is used by the team with the software [Obsidian](https://obsidian.md/), which offers a wide variety of tools and modules to plan, illustrate and organize our work and ideas. We set it up to work with Git using the community plugin of the same name, and typically also use the plugins `Excalidraw` and `Kanban`. We avoid using built-in canvas as they are a source of many conflicts with git merge protocol.

## Vizualisation

To view the data present on this branch in their original shape, you will need first to install Obsidian on your machine (from [website](https://obsidian.md/), flathub or other distributor). When done, launch it and create a new vault, which is and will take the form of a folder on your computer.

When the vault is opened, check the settings for "Community Plugins", which are user-developed features. Upon activating them, the browse button is accessible. Here are the ones we use:

- `git` for synchronisation
- `Kanban` for project planning and tasks listing

Download them to access our conception files, and enable them. Back in the general interface (exiting settings), press `ctrl + p` to open the command palette, and start entering this line in the search bar, to reveal the Git plugin commands:

```
Git: Clone an existing remote repo
```

Copy and paste our repository's link (regardless of the branch you're previewing), and press enter. In the field "Enter directory for clone, must be empty of nonexistent", enter precisely

```
pac-man
```

for paths consistency. Press enter again to skip clone depth, then wait for the cloning to be done. You will be prompted to restart Obsidian. Do so, but the files from the main branch will be present. Repress `ctrl + p` and enter:

```
Git: Switch branch
```

Select conception, and you should find this very README.md file inside the pac-man folder !

If so, you can now freely navigate our conception files and diagrams. Some files may need specific Community plugins, so go back to this README to find the list of plugins we used.