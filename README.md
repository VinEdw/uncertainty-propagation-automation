# uncertainty-propagation-automation

The goal of this project is to help automate calculations that require uncertainty propagation.

If $f(x_1, x_2, \ldots, x_n, \ldots, x_N)$ is a scalar valued function of $N$ parameters, then its uncertainty, $\Delta f$, is calculated with the following formula, where each $\Delta x_n$ is the uncertainty in that parameter.

$$\Delta f = \sqrt{
\left( \frac{\partial f}{\partial x_1} \Delta x_1 \right)^2 +
\left( \frac{\partial f}{\partial x_2} \Delta x_2 \right)^2 + \ldots
\left( \frac{\partial f}{\partial x_n} \Delta x_n \right)^2 + \ldots
\left( \frac{\partial f}{\partial x_N} \Delta x_N \right)^2
}
$$


The instructions for what to calculate, as well as the raw data, are provided by a `.json` file.
Sample input files can be found in `sample-json-input`.
Loosely, the structure is as follows.

```json
{
  // constants are useful for values that a user would like to reference repeatedly in their formulas
  "constants": [
    {
      "symbol": "g", // a valid identifier
      "value": 9.81, // a single number
      "uncertainty": 0, // a single number
      "units": "m/s^2" // a purely aesthetic string; the program does not check units
    }
    // More items can be added to the array as desired
  ],
  // inputs are the raw data that the program uses as a basis for calculation
  // They can be thought of as manually entered columns in a spreadsheet
  // Calculations using these items will be performed row by row
  "inputs": [
    {
      "symbol": "h", // a valid identifier
      "value": [
        10,
        20,
        30,
        40,
        50
      ], // an array of numbers
      "uncertainty": "sqrt (0.05**2 + (0.002 * h)**2)", // a formula to calculate the uncertainty
      "units": "cm" // a purely aesthetic string; the program does not check units
    }
    // More items can be added to the array as needed
    // Note that each item's value array should have the same length
  ],
  // outputs are the quantities calculated by the program
  // It propagates the uncertainty of the inputs in order to determine the uncertainty of the outputs
  // Note that outputs should be listed in the order that they should be calculated in
  // e.g. If the formula for B relies on the value for A, then A should be listed first
  "outputs": [
    {
      "symbol": "t", // a valid identifier
      "value": "sqrt(2 * (h/100) / (g))",
      "units": "s" // a purely aesthetic string; the program does not check units
    },
    {
      "symbol": "v_f",
      "value": "g * t",
      "units": "m/s"
    }
    // More items can be added to the array as needed
  ],
  // tables tells the program what tables to print out with input amd output items
  // If it is left empty, it defaults to a single table with each item in a column
  "tables": [
    ["h"], // a table with just h
    ["h", "t", "v_f"], // a table with everything
    ["v_f", "t"] // a table with just the outputs; note that the order can be switched here for printing
    // More table requests can be added to the array as needed
  ]
}
```

The simplest way to run the program, assuming all the needed Python packages have been installed, is with the following command.
> `python main.py input.json`

`input.json` should be replaced with the path to the desired input file. 
For the sample file used above (comments removed), the output is the following.
Note that the tables are using the markdown format.

```md
Trial | h (cm)
----- | -----------
1     | 10.0 ± 0.05
2     | 20.0 ± 0.06
3     | 30.0 ± 0.08
4     | 40.0 ± 0.09
5     | 50.0 ± 0.1

Trial | h (cm)      | t (s)           | v_f (m/s)
----- | ----------- | --------------- | -------------
1     | 10.0 ± 0.05 | 0.1428 ± 0.0004 | 1.401 ± 0.004
2     | 20.0 ± 0.06 | 0.2019 ± 0.0003 | 1.981 ± 0.003
3     | 30.0 ± 0.08 | 0.2473 ± 0.0003 | 2.426 ± 0.003
4     | 40.0 ± 0.09 | 0.2856 ± 0.0003 | 2.801 ± 0.003
5     | 50.0 ± 0.1  | 0.3193 ± 0.0004 | 3.132 ± 0.004

Trial | v_f (m/s)     | t (s)
----- | ------------- | ---------------
1     | 1.401 ± 0.004 | 0.1428 ± 0.0004
2     | 1.981 ± 0.003 | 0.2019 ± 0.0003
3     | 2.426 ± 0.003 | 0.2473 ± 0.0003
4     | 2.801 ± 0.003 | 0.2856 ± 0.0003
5     | 3.132 ± 0.004 | 0.3193 ± 0.0004
```

An alternate command can be run in order to get the tables output in the $\LaTeX$ format. 
> `python main.py input.json latex`

The table output uses column separators for decimal points and ± characters.
This helps with aligning the numbers in a column to those characters.
Other parts of the table syntax are from the [IOPScience document class](https://publishingsupport.iopscience.iop.org/questions/latex-template/) or custom macros to simplify stuff.
(Yes, I know the $\LaTeX$ stuff is specifically designed to work with my setup for Physics lab reports.
If I knew more about what people commonly do with $\LaTeX$, I might be able to design a more flexible system.)

Please let me know if you have any questions or suggestions.
Thank you.
