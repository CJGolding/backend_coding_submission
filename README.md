# Retail Spotlight Backend Challenge Submission
## By Caleb Golding

## Project Iterations
This challenge has gone through a couple of iterations:
- First iteration involved a functional approach, which did work, however it was not very abstract or easy to read.
- I then moved over to an object-oriented approach as it provided a greater level of abstraction and it allowed me to re-use certain areas of code. This iteration, however demonstrated tight coupling between product and sales data.
- My final iteration made the use of subclasses, processing product and brand data separately, while inheriting and/or overriding certain methods from the superclass. The superclass methods and attributes were set to protected where appropriate, and factory methods were used to call the constructor and other necessary methods in an attempt to achieve maximum encapsulation. While my final solution is rather verbose, it allows for a greater level of modularity and adaptability.

## Libraries and Data Structures Used
- The primary library is used was pandas (in conjunction with numpy). The DataFrame data structure in the pandas library has intuitive methods for reading csv files, manipulating data and converting to dictionaries, and it naturally seemed the best choice for tabular data.
- In order to be as efficient as possbile, I avoided using the apply function as it is computationally expensive due to perfoming row-wise operations. I primarily used np.where and pd.merge as an alternative as both pandas and numpy are optimised for vectorised, scalable operations, which these methods are.
- Even though pandas has a built-in to_json method, it did not seem appropriate to use it in this case, as the challenge first required that two different sets of datas were merged. I used the to_dict method to convert both dataframes into dictionaries first, then used the dump method from the simplejson library. I opted for simplejson over json as is easier to define certain requirements, such as ignoring nan values and setting them to null.
- One edge case my solution doesn't cover is when there is neither current or previous data present for the same date. If the required dates for the period were specified beforehand, then a template dataframe could have been made and merged. However, as no data in the set appeared to match the edge case, I felt implementing this would be beyond the scope of the challenge.

## Final Thoughts
- I am aware that only the run function was imported into the test_sample.py, however as I used several classes and functions, I thought it was more appropriate to import the whole python file, instead of picking out specific methods to import.
- I have seven unit tests, which all test the different capabilities of the program, and they all passed on my system.
- Likewise, the run function runs the program from beginning to end, producing a json file in an output directory in the specified format.
- If there are any issues when attempting to run/ test my program, please let me know.
- As a solution, I am aware it is probably more complex than it needs to be in some aspects, however as I am studying computer science, I wanted to take this opportunity to develop and practice some of my skills in OOP.
