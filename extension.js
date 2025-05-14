const vscode = require('vscode');
const path = require('path');
const { exec } = require('child_process');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
	console.log('✅ Extension "code-flow-doc-gen" is now active!');

	// Command: Generate Flowchart
	let generateFlowchart = vscode.commands.registerCommand('code-flow-doc-gen.generateFlowchart', function () {
		const editor = vscode.window.activeTextEditor;
		if (!editor) {
			vscode.window.showErrorMessage('No active file to process.');
			return;
		}

		const filePath = editor.document.fileName;
		const pyScript = path.join(context.extensionPath, 'flowchart_generator', 'run.py');

		exec(`python "${pyScript}" flowchart "${filePath}"`, (err, stdout, stderr) => {
			if (err) {
				console.error(stderr);
				vscode.window.showErrorMessage(`❌ Flowchart generation failed.`);
			} else {
				console.log(stdout);
				vscode.window.showInformationMessage('✅ Flowchart generated successfully.');
			}
		});
	});

	// Command: Generate Documentation
	let generateDoc = vscode.commands.registerCommand('code-flow-doc-gen.generateDoc', function () {
		const editor = vscode.window.activeTextEditor;
		if (!editor) {
			vscode.window.showErrorMessage('No active file to process.');
			return;
		}

		const filePath = editor.document.fileName;
		const pyScript = path.join(context.extensionPath, 'flowchart_generator', 'run.py');

		exec(`python "${pyScript}" doc "${filePath}"`, (err, stdout, stderr) => {
			if (err) {
				console.error(stderr);
				vscode.window.showErrorMessage(`❌ Documentation generation failed.`);
			} else {
				console.log(stdout);
				vscode.window.showInformationMessage('✅ Documentation generated successfully.');
			}
		});
	});

	context.subscriptions.push(generateFlowchart, generateDoc);
}

function deactivate() {}

module.exports = {
	activate,
	deactivate
}
