'use strict'

const readline = require('readline')

const parseSCIPSolution = (solutionStream) => {
    return new Promise((resolve, reject) => {
        const solution = {}
        const rl = readline.createInterface({
            input: solutionStream,
            crlfDelay: Infinity
        })

        rl.on('line', (line) => {
            // SCIP solution format is:
            // objective value: <value>
            // <variable> <value>
            // <variable> <value>
            // ...
            if (!line.startsWith('objective value:')) {
                const [variable, value] = line.trim().split(/\s+/)
                if (variable && value) {
                    solution[variable] = parseFloat(value)
                }
            }
        })

        rl.on('close', () => {
            resolve(solution)
        })

        rl.on('error', (err) => {
            reject(err)
        })
    })
}

module.exports = parseSCIPSolution 
