import numpy as np
import pandas as pd
import itertools
import time
import os
from IPython.display import clear_output


def in_notebook():
    try:
        from IPython import get_ipython
        if 'IPKernelApp' not in get_ipython().config:  # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True

class Sudoku:

    def __init__(self,data=None):
        self.board = np.zeros((9,9),np.int16) if data is None else data
        self.boxes = self.get_boxes()
        self.info_arr = self.get_info_arr()
        self.board_flat = self.board.flatten()
        self.info_iter = iter(np.argsort(self.info_arr.flatten())[::-1])
        self.start_time = time.time()
        self.is_notebook = in_notebook()
        self.finished = False

    def __repr__(self):
        string = '''
        {} {} {}|{} {} {}|{} {} {}
        {} {} {}|{} {} {}|{} {} {}
        {} {} {}|{} {} {}|{} {} {}
        -----------------
        {} {} {}|{} {} {}|{} {} {}
        {} {} {}|{} {} {}|{} {} {}
        {} {} {}|{} {} {}|{} {} {}
        -----------------
        {} {} {}|{} {} {}|{} {} {}
        {} {} {}|{} {} {}|{} {} {}
        {} {} {}|{} {} {}|{} {} {}'''
        return string.format(*self.board_flat)

    def reset(self):
        self.__init__()

    def load_gamestate(self,string):
        board_ = list(int(i) for i in string)
        board_ = np.reshape(board_,(9,9))
        self.board = board_
        self.board_flat = self.board.flatten()
        self.info_arr = self.get_info_arr()
        self.boxes = self.get_boxes()
        self.update_board()

    def get_boxes(self):
        boxes = list()
        for i in np.arange(0,9,3):
            for j in np.arange(0,9,3):
                box = self.board[i:i+3,j:j+3]
                boxes.append(box)
        return boxes

    def coord_to_idx(self,x,y):
        return 9*y + x

    def idx_to_coord(self,idx):
        return  idx%9, int(np.floor(idx / 9))

    def find_box(self,x,y,idx=True):
        row_pos = int(np.floor(x / 3))
        col_pos = int(np.floor(y / 3))
        result = 3*col_pos + row_pos if idx else (row_pos,col_pos)

        return result

    def get_box_coords(self,box_number):
        vals = [0,3,6]
        itertools.combinations()
        
    def get_info_arr(self):
        info = []
        for i in range(9):
            for j in range(9):
                if self.board[i,j] != 0:
                    info.append(0)
                    continue
                row = self.board[i,:]
                col = self.board[:,j]
                box = self.boxes[self.find_box(j,i)].flatten()
                knowns = np.unique(np.concatenate((row,col,box)))
                knowns = np.delete(knowns,np.where(knowns==0))
                info_ = len(knowns)/9
                info.append(info_)
        info = np.array(info).reshape((9,9))

        return info

    def get_knowns(self,x,y):
        row = self.board[y,:]
        col = self.board[:,x]
        box = self.boxes[self.find_box(x,y)].flatten()
        knowns = np.unique(np.concatenate((row,col,box)))
        knowns = np.delete(knowns,np.where(knowns==0))
        return knowns

    def get_possibles(self,x,y):
        knowns = self.get_knowns(x,y)
        poss = np.array([i for i in np.arange(1,10) if i not in knowns])
        return poss

    def solve(self,verbose=True,wait_period=0.025,override_wait=False):
        wait_period = 0.125 if self.is_notebook and not override_wait else wait_period
        indeces = list(np.argsort(self.info_arr.flatten())[::-1])
        solved = False
        it = 0

        while not solved and not self.finished:
            idx = indeces[it]
            if self.info_arr.flatten()[idx]==0:
                nonzeros = [indx for indx in indeces if self.board_flat[indx] == 0]
                idx = nonzeros[0]

            coord = self.idx_to_coord(idx)
            sol_arr = [n for n in np.arange(1,10) if self.check(idx,n)]
            time.sleep(wait_period)

            if len(sol_arr)==1 and self.check(idx,sol_arr[0]):
                sol = sol_arr[0]
                
            else:
                fits = [None]*10
                for sol_ in sol_arr:
                    fits[sol_] = self.check_neighbors(idx,sol_)
                try:
                    sol = fits.index(1)
                except:
                    it += 1
                    continue

            self.board_flat[idx] = sol
            self.update_board()
            if verbose:
                if self.is_notebook and not self.finished:
                    clear_output(wait=True)
                elif not self.is_notebook and not self.finished:
                    os.system('clear')
                print(f'Position {coord} is {sol}')
                print(self.__repr__())
                print(f'{81-sum(self.board_flat==0)}/81 values found in {round(time.time()-self.start_time,3)} seconds')
            del idx
            solved = True
            if not any(self.board_flat==0):
                self.finished = True
        
        if not self.finished:
            self.solve()
        else:
            print('Solution found!')

    def update_board(self):
        self.board = self.board_flat.reshape((9,9))
        self.info_arr = self.get_info_arr()
        self.info_iter = iter(np.argsort(self.info_arr.flatten())[::-1])
        self.boxes = self.get_boxes()

    def check_neighbors(self,idx,val: int):
        x, y = self.idx_to_coord(idx)
        box_coord = self.find_box(x,y,idx=False)
        xs = range(3*box_coord[0],3*box_coord[0]+3)
        ys = range(3*box_coord[1],3*box_coord[1]+3)
        coords = list(itertools.product(xs,ys))

        possibs = [self.check(self.coord_to_idx(*p),val) for p in coords]
        
        return sum(possibs)

    def check(self,idx,val: int):
        x, y = self.idx_to_coord(idx)
        row = self.board[y,:]
        col = self.board[:,x]
        box = self.boxes[self.find_box(x,y)].flatten()

        conds = [
                 val in row,
                 val in col,
                 val in box
                ]

        if any(conds):
            return False
        else:
            return True

    def double_check(self):
        '''Simple check on no duplicates on rows, columns, and squares'''
        checks = [not self.check(idx,self.board_flat[idx]) for idx in range(81)]
        return all(checks)
        
    def to_string_format(self):
        string = ''.join([str(i) for i in self.board_flat])
        return string




if __name__ == '__main__':
    df = pd.read_csv('sudoku_games.csv')

    random_quiz = np.random.randint(0,df.quizzes.count()-1)
    gamestate = df.quizzes[random_quiz]

    s = Sudoku()
    s.load_gamestate(gamestate)
    s.solve(wait_period=0)
    print(f'Quiz #{random_quiz}')
    