
import time

# =====================================================
# CSP MODEL
# =====================================================

class SudokuCSP:

    def __init__(self,puzzle):


        self.variables=[]

        self.domains={}

        self.neighbors={}


        # Variables

        for r in range(9):

            for c in range(9):

                self.variables.append((r,c))


        # Domains

        for r,c in self.variables:


            value=int(puzzle[r*9+c])


            if value==0:

                self.domains[(r,c)] = set(range(1,10))

            else:

                self.domains[(r,c)] = {value}



        # Neighbors

        for var in self.variables:

            self.neighbors[var]=self.get_neighbors(var)



        # Statistics

        self.nodes_expanded=0

        self.backtracks=0

    def get_neighbors(self,var):


        r,c=var


        result=set()

        # Row
        for col in range(9):

            if col!=c:

                result.add((r,col))


        # Column

        for row in range(9):

            if row!=r:

                result.add((row,c))


        # Box

        br=(r//3)*3

        bc=(c//3)*3


        for i in range(br,br+3):

            for j in range(bc,bc+3):

                if (i,j)!=var:

                    result.add((i,j))


        return result





    def is_consistent(self,var,value,assignment):


        for n in self.neighbors[var]:


            if n in assignment:

                if assignment[n]==value:

                    return False


        return True





# =====================================================
# AC-3 ALGORITHM
# =====================================================


class AC3:



    def __init__(self,csp):

        self.csp=csp





    def revise(self,Xi,Xj):


        revised=False


        remove=[]


        for x in self.csp.domains[Xi]:


            supported=False


            for y in self.csp.domains[Xj]:


                if x!=y:

                    supported=True

                    break



            if not supported:

                remove.append(x)




        for x in remove:

            self.csp.domains[Xi].remove(x)

            revised=True



        return revised





    def run(self):


        queue=[]



        # all arcs

        for Xi in self.csp.variables:

            for Xj in self.csp.neighbors[Xi]:

                queue.append((Xi,Xj))



        while queue:


            Xi,Xj=queue.pop(0)



            if self.revise(Xi,Xj):


                if len(self.csp.domains[Xi])==0:

                    return False



                for Xk in self.csp.neighbors[Xi]:

                    if Xk!=Xj:

                        queue.append((Xk,Xi))


        return True





# =====================================================
# BACKTRACKING + MRV
# =====================================================



class Solver:



    def __init__(self,csp,use_mrv=True):


        self.csp=csp

        self.use_mrv=use_mrv





    def select_variable(self,assignment):


        remaining=[

            v for v in self.csp.variables

            if v not in assignment

        ]



        if not self.use_mrv:

            return remaining[0]



        # MRV

        return min(

            remaining,

            key=lambda x:

            len(self.csp.domains[x])

        )







    def forward_check(self,var,value):


        removed={}



        for neighbor in self.csp.neighbors[var]:


            if value in self.csp.domains[neighbor]:


                self.csp.domains[neighbor].remove(value)



                removed.setdefault(
                    neighbor,
                    []
                ).append(value)



                if len(self.csp.domains[neighbor])==0:

                    return None



        return removed






    def restore(self,removed):


        if removed:

            for var,values in removed.items():

                for v in values:

                    self.csp.domains[var].add(v)






    def backtrack(self,assignment):



        # goal test

        if len(assignment)==81:

            return assignment




        var=self.select_variable(assignment)



        for value in list(self.csp.domains[var]):



            # count node expansion

            self.csp.nodes_expanded+=1



            if self.csp.is_consistent(
                var,
                value,
                assignment
            ):


                assignment[var]=value



                removed=self.forward_check(
                    var,
                    value
                )



                if removed is not None:


                    result=self.backtrack(
                        assignment
                    )


                    if result:

                        return result




                self.restore(removed)


                del assignment[var]



            self.csp.backtracks+=1



        return None







# =====================================================
# FILE HANDLING
# =====================================================


def convert_solution(solution):


    result=""


    for r in range(9):

        for c in range(9):

            result+=str(solution[(r,c)])


    return result






def solve_file(input_file,output_file,use_mrv=True):



    with open(input_file) as f:


        puzzles=[
            x.strip()
            for x in f
            if x.strip()
        ]



    answers=[]




    for puzzle in puzzles:



        print("\n======================")

        print("Solving puzzle")



        start=time.time()



        csp=SudokuCSP(puzzle)



        # AC-3

        AC3(csp).run()



        solver=Solver(
            csp,
            use_mrv
        )



        solution=solver.backtrack({})



        end=time.time()




        if solution:


            answers.append(
                convert_solution(solution)
            )


            print("Solved")

            print(
                "Time:",
                end-start
            )

            print(
                "Nodes Expanded:",
                csp.nodes_expanded
            )

            print(
                "Backtracks:",
                csp.backtracks
            )



        else:

            answers.append(
                "NO SOLUTION"
            )





    with open(output_file,"w") as f:


        for a in answers:

            f.write(a+"\n")





# =====================================================
# MAIN
# =====================================================



if __name__=="__main__":


    print("Sudoku CSP Solver")


    solve_file(
        "puzzles.txt",
        "solutions.txt",
        use_mrv=False
    )