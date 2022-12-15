## From Labour_Model_Hours to Shifts

### Steps
#### 1. Visualising the Data
As a first thing we have received a rule set that allow us to translate the guest_count in an ideal number that fit the needs of the General Managers from the sites.

We know that for a x number of guest we have a y ideal number of employees for each departments.


Tha information allow us to visualise that need in a plot.
I took the data from dd/mm/yyyy of the King's Cross Expeditor Team.

The X axis represents the hours in a regular day of work, and the Y axis is indicating the number of employees needed.

#### 2. Understanding the totals
The second step is to visualise how many hours the sites actually needs for that day, (knowing that a 5% margin of error is allowed? Thanks to the budget?).

The same graph can be represented in a different format to have a better understanding of the totals.

[[Button_Totals]]

We can now see a representation of the same graph and we can identify the totals just counting how many red bricks are on the graph.

Usually we represent timeseries counting the y value vertically to get the total, like the blue bricks. That would be the total for that hour.

#### 3. Everything in the right form
Add minimum hours and maximum hours give us the informations we need to identify all the possible shift lentgh.

[[Show_Shifts]]

We can observe the shift being a set of briks horizontally aligned.
So we are going to count the totals in a horizontal way to make a first step towards the translation.

[[Horizontal_Count]]

We can observe that the same graph now can already gives us some insight.

We can see that some layers are being crated and have a more similar shape to the shift that we need find.

Appear clear that in this form the layers still are unusable for a translation, they are too long sometimes.

To solve this problem we need to split the layers in usable chunks of hours that fit the sizes of the possible shifts, an information that we already have.

We can decompose the layers into shifts. 
And now we have a list of shifts that we need to cover.



