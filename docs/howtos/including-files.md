# Including Files in Documentation

This guide demonstrates how to include content from other files in your documentation using the MyST include directive.

## Using the Include Directive

You can include files in Sphinx documentation using the `include` directive with MyST syntax:

````markdown
```{include} ../README.md
```
````

## Example: Project README

Below is an example of including the project README file:

```{include} ../../README.md
```

## Benefits

- **DRY Principle**: Avoid duplicating content between your README and documentation
- **Consistency**: Keep information synchronized across files
- **Maintenance**: Update once, reflect everywhere

## Relative Paths

The include directive uses paths relative to the current file. For example:
- `../README.md` - goes up one directory
- `../../README.md` - goes up two directories
- `./file.md` - same directory

## Tips

- Use includes for shared content like installation instructions, contribution guidelines, or license information
- Be mindful of heading levels when including content
- Test your documentation build to ensure paths are correct
