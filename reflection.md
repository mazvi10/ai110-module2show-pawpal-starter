# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    
    My three core actions were adding a pet, setting a task and displaing the day's tasks

- What classes did you include, and what responsibilities did you assign to each?

    I included Pet, Owner, Task and Scheduler classes.
    
    For the Pet class, I included name, animal_type, age and tasks attributes
    For the Owner class, I included name and pet_list attributes
    For the Scheduler class, I included time_available and pet_list attributes
    For the Task class, I included description, due_date, priority and status attributes

    For the Pet class, I included  add_task and delete_task methods
    For the Owner class, I included add_pet and delete_pet methods
    For the Scheduler class, I included sort_by_priority, get_single_pet_tasks, explain_plan, generate_plan and format_schedule methods
    For the Task class, I included a mark_complete method



**b. Design changes**

- Did your design change during implementation?

    Yes, it did

- If yes, describe at least one change and why you made it.

    I evolved my original four-class design by adding a PlanEntry object, making the Scheduler read pets directly from the Owner, and storing the generated plan as state so explanation and display don't recompute it.




---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

    My scheduler considers priority first then futher sorts using time second

- How did you decide which constraints mattered most?

    I thought of it practically as higher priority tasks should always been done first, at least ideally

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

    My scheduler sorts according to priority first, thus even a long high priority task can finish up all the required time before lower prority tasks can take place

- Why is that tradeoff reasonable for this scenario?

    It is reasonable as if the task is very important, indicated by the priority ranking, it will be done for the pet and the more mundane ones can be sacrificed, especially in real life situations e.g. if a pet needs meds and feeding without having time for playing if the pet is sick and the other tasks matter more

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

    I mainly used for refactoring and debudgging

- What kinds of prompts or questions were most helpful?

    The most helpful prompts were the ones sorting out the relationships within my UML as that cleared up any errors that would have jumbled up my methods and attributes in the future, making everything compact

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

    I did not accept the AI's suggestion for handling recurrences as it over complicated the interface for the user. Rather, I let the scheduler give the user an option of making it recurring or catching a trend if a task is repeated

- How did you evaluate or verify what the AI suggested?

    I evaluated it by checking every suggestion before it was implemented instead of just letting the AI change everything, and I also made sure to have a plan to refer back to when checking the AI suggestions

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

    I tested happy runs and edge cases, focussing on recurrences, filtering and sorting

- Why were these tests important?

    They were important as they tested the main functionality of the scheduler, which is the point of the app

**b. Confidence**

- How confident are you that your scheduler works correctly?

    I am quite confident, but a little more polishing never hurt anyone ;)

- What edge cases would you test next if you had more time?

    I would further test going between multiple owners 

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

    I am most satisfied with the class and object interactions

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

    I would improve my plan explanation section and make it less wordy

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

    Sorting out object interactions really helps clean up the code and makes the workflow more streamlined
