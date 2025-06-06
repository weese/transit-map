#!/usr/bin/env node
'use strict'

const l = require('lodash')
const mri = require('mri')
const getStdin = require('get-stdin')
const writeFile = require('write')
const graphToSVG = require('svg-transit-map')
const svgToString = require('virtual-dom-stringify')
const { Writable } = require('stream')

const transitMap = require('.')
const prepareGraph = require('./prepare-graph')
const createGenerateLP = require('./generate-lp')
const pkg = require('./package.json')

const SETTINGS = {
	offset: 10000,
	maxWidth: 300,
	maxHeight: 300,
	minEdgeLength: 1,
	maxEdgeLength: 8
}

const argv = mri(process.argv.slice(2), {
	boolean: ['help', 'h', 'version', 'v', 'silent', 's', 'graph', 'g', 'invert-y', 'y', 'debug', 'd']
})

if (argv.help === true || argv.h === true) {
	process.stdout.write(`
transit-map [options]

Usage:
	cat graph.json | transit-map > network.json

Options:
	--tmp-dir      -t  Directory to store intermediate files. Default: unique tmp dir.
	--output-file  -o  File to store result (instead of stdout).
	--silent       -s  Disable solver logging to stderr.
	--graph        -g  Return JSON graph instead of SVG map.
	--invert-y     -y  Invert the Y axis in SVG result.
	--debug        -d  Output the generated LP and stop.

	--help         -h  Show this help message.
	--version      -v  Show the version number.

`)
	process.exit(0)
}

if (argv.version === true || argv.v === true) {
	process.stdout.write(`${pkg.version}\n`)
	process.exit(0)
}

// main program

const config = {
	workDir: argv['tmp-dir'] || argv.t || null,
	verbose: !(argv.silent || argv.s || null),
	outputFile: argv['output-file'] || argv.o || null,
	returnGraph: argv['graph'] || argv.g || false,
	invertY: argv['invert-y'] || argv.y || false,
	debug: argv['debug'] || argv.d || false
}

const main = async () => {
	const stdin = await getStdin()
	if (!stdin) throw new Error('No input network found in stdin.')
	const graph = JSON.parse(stdin)

	if (config.debug) {
		const preparedGraph = prepareGraph(graph)
		const generateLP = createGenerateLP(preparedGraph, SETTINGS)
		let lp = ''
		const stream = new Writable({
			write(chunk, encoding, callback) {
				lp += chunk.toString()
				callback()
			}
		})
		generateLP(stream)
		if (config.outputFile) await writeFile(config.outputFile, lp)
		else process.stdout.write(lp)
		process.exit(0)
	}

	const solution = await transitMap(graph, l.pick(config, ['workDir', 'verbose']))

	let result
	if (config.returnGraph) result = JSON.stringify(graph)
	else {
		const svg = graphToSVG(solution, config.invertY)
		result = svgToString(svg)
	}

	if (config.outputFile) await writeFile(config.outputFile, result)
	else process.stdout.write(result)
}

main()
.catch((err) => {
	console.error(err)
	process.exitCode = 1
})
