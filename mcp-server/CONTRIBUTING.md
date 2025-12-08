# Contributing to Lightsail Deployment MCP Server

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/naveenraj44125-creator/lamp-stack-lightsail.git
cd lamp-stack-lightsail/mcp-server
```

2. Install dependencies:
```bash
npm install
```

3. Run tests:
```bash
./test.sh
```

## Project Structure

```
mcp-server/
├── index.js           # Main MCP server implementation
├── package.json       # NPM package configuration
├── README.md          # Main documentation
├── INSTALL.md         # Installation guide
├── EXAMPLES.md        # Usage examples
├── QUICKSTART.md      # Quick start guide
├── CHANGELOG.md       # Version history
├── test.sh            # Test script
└── .npmignore         # NPM ignore file
```

## Adding a New Tool

1. Add tool definition in `setupToolHandlers()`:

```javascript
{
  name: 'your_tool_name',
  description: 'What your tool does',
  inputSchema: {
    type: 'object',
    properties: {
      param1: {
        type: 'string',
        description: 'Parameter description',
      },
    },
    required: ['param1'],
  },
}
```

2. Add tool handler in the switch statement:

```javascript
case 'your_tool_name':
  return await this.yourToolMethod(args);
```

3. Implement the method:

```javascript
async yourToolMethod(args) {
  const { param1 } = args;
  
  // Your implementation
  
  return {
    content: [
      {
        type: 'text',
        text: 'Result message',
      },
    ],
  };
}
```

4. Update documentation:
   - Add to README.md
   - Add examples to EXAMPLES.md
   - Update CHANGELOG.md

## Testing Your Changes

1. Run the test suite:
```bash
./test.sh
```

2. Test manually with MCP Inspector:
```bash
npx @modelcontextprotocol/inspector node index.js
```

3. Test with your AI assistant:
```bash
npm link
# Restart your AI assistant
# Test the new tool
```

## Code Style

- Use ES6+ features
- Use async/await for asynchronous operations
- Add JSDoc comments for public methods
- Keep functions focused and single-purpose
- Handle errors gracefully

## Error Handling

Always wrap tool implementations in try-catch:

```javascript
try {
  // Your implementation
  return {
    content: [{ type: 'text', text: 'Success message' }],
  };
} catch (error) {
  return {
    content: [{ type: 'text', text: `Error: ${error.message}` }],
    isError: true,
  };
}
```

## Documentation

When adding features:

1. Update README.md with tool description
2. Add usage examples to EXAMPLES.md
3. Update CHANGELOG.md with changes
4. Add installation notes if needed

## Commit Messages

Use conventional commit format:

- `feat: Add new tool for X`
- `fix: Resolve issue with Y`
- `docs: Update README with Z`
- `test: Add tests for W`
- `refactor: Improve V implementation`

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `./test.sh`
5. Commit with descriptive messages
6. Push to your fork
7. Create a Pull Request

### PR Checklist

- [ ] Tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No syntax errors
- [ ] Code follows style guidelines
- [ ] Examples added if applicable

## Feature Requests

Have an idea? Open an issue with:

- Clear description of the feature
- Use case and benefits
- Example usage
- Any implementation ideas

## Bug Reports

Found a bug? Open an issue with:

- Description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (Node.js version, OS, etc.)

## Questions?

- Open a GitHub issue
- Check existing documentation
- Review examples in EXAMPLES.md

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions professional

Thank you for contributing! 🎉
