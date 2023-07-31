"""Implement Expected Threat Model"""

import json
import os
from typing import Callable, List, Optional, Tuple
import numpy as np
import numpy.typing as npt
import pandas as pd
from pandera.typing import DataFrame, Series
from sklearn.exceptions import NotFittedError

from scipy.interpolate import interp2d

from mplfooty.pitch import Pitch

pitch_length = 165
pitch_width = 135

x_bins = 40
y_bins = 32
bins = (x_bins, y_bins)

def _get_cell_indexes(
    x: Series[float], y: Series[float], l: int = x_bins, w: int = y_bins
) -> Tuple[Series[int], Series[int]]:
    xi = x.divide(pitch_length).multiply(l)
    yi = y.divide(pitch_width).multiply(w)
    
    xi = xi.astype("int64").clip(-l/2, l/2)
    yi = yi.astype("int64").clip(-w/2, w/2)
    
    xi, yi = (xi+(l/2-1)).astype(int).clip(0, l-1), (yi+(w/2-1)).astype(int).clip(0, w-1)
    
    return xi, yi

def _get_flat_indexes(x: Series[float], y: Series[float], l: int = x_bins, w: int = y_bins) -> Series[int]:
    xi, yi = _get_cell_indexes(x, y, l, w)
    return l * (w - 1 - yi) + xi

def _count(x: Series[float], y: Series[float], l: int = x_bins, w: int = y_bins) -> npt.NDArray[np.int_]:
    """ Count the number of actions occurring in each cell of the grid.
    
    Parameters
    ----------
    x : pd.Series
        The x-coordinates of the actions.
    y : pd.Series
        The y-coordinates of the actions.
    l : int
        Amount of grid cells in the x-dimension of the grid.
    w : int
        Amount of grid cells in the y-dimension of the grid.
    
    Returns
    -------
    np.ndarray
        A matrix, denoting the amount of actions occurring in each cell.
        The centre is the origin.
        
    """
    
    x = x[~np.isnan(x) & ~np.isnan(y)]
    y = y[~np.isnan(x) & ~np.isnan(y)]
    
    flat_indexes = _get_flat_indexes(x, y, l, w)
    vc = flat_indexes.value_counts(sort=False)
    vector = np.zeros(w * l, dtype=int)
    vector[vc.index] = vc
    return vector.reshape((w, l))

def _safe_divide(a: npt.ArrayLike, b: npt.ArrayLike) -> npt.NDArray[np.float64]:
    return np.divide(a, b, out=np.zeros_like(a, dtype="float64"), where=b != 0, casting = "unsafe")

def scoring_prob(actions: DataFrame, l: int=x_bins, w: int=y_bins) -> npt.NDArray[np.float64]:
    """ Compute the probability of scoring when taking a shot for each cell.

    Parameters
    ----------
    actions : DataFrame
        Actions
    l : int
        Amount of grid cells in the x-dimension of the grid.
    w : int
        Amount of grid cells in the y-dimension of the grid.

    Returns
    -------
    npt.NDArray
        A matrix, denoting the probability of scoring for each cell.
    """
    shot_actions = actions[(actions['type_name'] == "Shot")]
    goals = shot_actions[(actions['goal'] == True)]
    
    shot_matrix = _count(shot_actions['x'], shot_actions['y'], l, w)
    goal_matrix = _count(goals['x'], goals['y'], l, w)
    return _safe_divide(goal_matrix, shot_matrix)

def get_move_actions(actions: DataFrame) -> DataFrame:
    """Get all ball-progressing actions.

    Parameters
    ----------
    actions : DataFrame
        Actions

    Returns
    -------
    DataFrame
        All ball-progressing actions in the input dataframe.
    """
    return actions[(actions['type_name']=="Handball") | (actions['type_name'] == "Kick") | (actions['type_name'] == "Carry")]

def get_successful_move_actions(actions: DataFrame) -> DataFrame:
    """ Get all successful ball-progressin actions.

    Parameters
    ----------
    actions : DataFrame
        Actions

    Returns
    -------
    DataFrame
        All successful ball-progressing actions in the input dataframe.
    """
    
    move_actions = get_move_actions(actions)
    return move_actions[move_actions['outcome_name'] == True]

def action_prob(actions: DataFrame, l: int=x_bins, w: int=y_bins) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """_summary_

    Parameters
    ----------
    actions : DataFrame
        Actions
    l : int
        Amount of grid cells in the x-dimension of the grid.
    w : int
        Amount of grid cells in the y-dimension of the grid.

    Returns
    -------
    shot_matrix: np.ndarray
        For each cell, the probability of choosing to shoot.
    move_matrix: np.ndarray
        For each cell, the probability of choosing to move.
    """
    
    move_actions = get_move_actions(actions)
    shot_actions = actions[(actions['type_name'] == "Shot")]
    
    move_matrix = _count(move_actions['x'], move_actions['y'], l, w)
    shot_matrix = _count(shot_actions['x'], shot_actions['y'], l, w)
    total_matrix = move_matrix + shot_matrix
    
    return _safe_divide(shot_matrix, total_matrix), _safe_divide(move_matrix, total_matrix)

def move_transition_matrix(actions: DataFrame, l: int=x_bins, w: int=y_bins
                           ) -> npt.NDArray[np.float64]:
    """Compute the move transition matrix from the given actions.
    
    This is, when a player chooses to move, the probbility that he will end up
    in each of the other cells of the grid successfully.

    Parameters
    ----------
    actions : DataFrame
        Actions
    l : int
        Amount of grid cells in the x-dimension of the grid.
    w : int
        Amount of grid cells in the y-dimension of the grid.

    Returns
    -------
    np.ndarray
        The move transition matrix
    """
    
    move_actions = get_move_actions(actions)
    
    X = pd.DataFrame()
    X['start_cell'] = _get_flat_indexes(move_actions['x'], move_actions['y'], l, w)
    X['end_cell'] = _get_flat_indexes(move_actions['end_x'], move_actions['end_y'], l, w)
    X['outcome'] = move_actions['outcome_name']
    
    vc = X['start_cell'].value_counts(sort=False)
    start_counts = np.zeros(w * l)
    start_counts[vc.index] = vc
    
    transition_matrix = np.zeros((w * l, w * l))
    
    for i in range(0, w * l):
        vc2 = X[(X['start_cell'] == i) & (X['outcome'] == True)]['end_cell'].value_counts(sort=False)
        transition_matrix[i, vc2.index] = vc2 / start_counts[i]
        
    return transition_matrix

class ExpectedThreat:
    """An implementation of the Expected Threat (xT) model.
    
    The xT model [1] can be used to value actions that successfully move the ball 
    between two locations on the pitch by computing the difference between the 
    long-term probability of scoring on the start and end location of an action.
    
    Parameters
    ----------
    l : int
        Amount of grid cells in the x-dimension of the grid.
    w : int
        Amount of grid cells in the y-dimension of the grid.
    eps: float
        The desired precision to calculate xT value of a cell. Default is 5 dp.
        
    Attributes
    ----------
    
    
    
    References
    ----------
    .. [1] 
    
    """
    def __init__(self, l: int=x_bins, w: int=y_bins, eps: float = 1e-5) -> None:
        self.l = l
        self.w = w
        self.eps = eps
        self.heatmaps: List[npt.NDArray[np.float64]] = []
        self.xT: npt.NDArray[np.float64] = np.zeros((self.w, self.l))
        self.scoring_prob_matrix: Optional[npt.NDArray[np.float64]] = None
        self.shot_prob_matrix: Optional[npt.NDArray[np.float64]] = None
        self.move_prob_matrix: Optional[npt.NDArray[np.float64]] = None
        self.transition_matrix: Optional[npt.NDArray[np.float64]] = None
        
    def __solve(
        self, 
        p_scoring: npt.NDArray[np.float64],
        p_shot: npt.NDArray[np.float64],
        p_move: npt.NDArray[np.float64],
        transition_matrix: npt.NDArray[np.float64]
    ) -> None:
        """Solves the expected threat equation with dynamic programming.

        Parameters
        ----------
        p_scoring : (np.ndarray, shape(y_bins, x_bins)):
            When shooting from that cell, probability of scoring.
        p_shot : (np.ndarray, shape(y_bins, x_bins)):
            For each grid cell, the probability of choosing to shoot from there.
        p_move : (np.ndarray, shape(y_bins, x_bins)):
            For each grid cell, the probability of choosing to move from there.
        transition_matrix : (np.ndarray, shape((y_bins, x_bins), (y_bins, x_bins)):
            When moving, the probability of moving to each of the other zones.
        """
        goal_scoring_prob = p_scoring * p_shot
        diff = np.ones((self.w, self.l), dtype=np.float64)
        iterations = 0
        self.heatmaps.append(self.xT.copy())
        
        while np.any(diff > self.eps):
            total_payoff = np.zeros((self.w, self.l), dtype=np.float64)
            
            for y in range(0, self.w):
                for x in range(0, self.l):
                    for q in range(0, self.w):
                        for z in range(0, self.l):
                            total_payoff[y, x] += (
                                transition_matrix[self.l * y + x, self.l * q + z] * self.xT[q, z]
                            )
                            
            new_xT = goal_scoring_prob + (p_move * total_payoff)
            diff = new_xT - self.xT
            self.xT = new_xT
            self.heatmaps.append(self.xT.copy())
            
            iterations += 1
            
        print("# iterations: ", iterations)
        
    def fit(self, actions: DataFrame) -> "ExpectedThreat":
        """ Fits the xT model with the given actions.

        Parameters
        ----------
        actions : DataFrame
            Actions

        Returns
        -------
        self
            Fitted xT model
        """
        self.scoring_prob_matrix = scoring_prob(actions, self.l, self.w)
        self.shot_prob_matrix, self.move_prob_matrix = action_prob(actions, self.l, self.w)
        self.transition_matrix = move_transition_matrix(actions, self.l, self.w)
        self.xT = np.zeros((self.w, self.l))
        self.__solve(
            self.scoring_prob_matrix,
            self.shot_prob_matrix,
            self.move_prob_matrix,
            self.transition_matrix
        )
        return self
    
    def interpolator(
        self, kind: str="linear"
    ) -> Callable[[npt.NDArray[np.float], npt.NDArray[np.float]], npt.NDArray[np.float]]:
        """Interpolate over the pitch.

        Parameters
        ----------
        kind : {'linear', 'cubic', 'quintic'}
            The kind of spline interpolation to use, by default "linear"

        Returns
        -------
        Callable
            A function that interpolates xT values over the pitch.
        """
        
        if interp2d is None:
            raise ImportError("Interpolation requires scipy.")
        
        cell_length = pitch_length / self.l
        cell_width = pitch_width / self.w
        
        x = np.arange(0,0,pitch_length,cell_length) + 0.5*cell_length
        y = np.arange(0,0,pitch_width,cell_width) + 0.5*cell_width
        
        return interp2d(x=x, y=y, z=self.xT, kind=kind, bounds_error=False)
        
    def rate(
        self, actions: DataFrame, use_interpolation: bool = False) -> npt.NDArray[np.float64]:
        """ Compute the xT values for the given actions.
        
        xT should only be used to value actions that move the ball
        and keep the current team in possession of the ball. ALl
        other actions in the given dataframe receive a 'NaN' rating.
        
        Parameters
        ----------
        actions: DataFrame
            Actions
        use_interpolation : bool
            Indicates whether to use bilinear interpolation when
            inferring xT values.
        
        Raises
        ------
        NotNotFittedError
            If the model has not been fitted yet.
            
        Returns
        -------
        np.ndarray
            The xT value for each action.
        
        """
        
        if not np.any(self.xT):
            raise NotFittedError()
        
        if not use_interpolation:
             l = self.l
             w = self.w
             grid = self.xT
        else:
            #use interpolation to create a more fine-grained grid
            interp = self.interpolator()
            l = int(pitch_length * 10)
            w = int(pitch_width * 10)
            xs = np.linspace(0, pitch_length, l)
            ys = np.linspace(0, pitch_width, w)
            grid = interp(xs, ys)
        
        ratings = np.empty(len(actions))
        ratings[:] = np.NaN
        
        move_actions = get_successful_move_actions(actions.reset_index())
        
        startxc, startyc = _get_cell_indexes(move_actions['x'], move_actions['y'], l, w)
        endxc, endyc = _get_cell_indexes(move_actions['end_x'], move_actions['end_y'], l, w)
        
        xT_start = grid[startyc.rsub(w - 1), startxc]
        xT_end = grid[endyc.rsub(w-1), endxc]
        
        ratings[move_actions.index] = xT_end - xT_start
        return ratings
    
    def save_model(self, file_path:str, overwrite : bool = True) -> None:
        """Save the xT value surface in JSON format
        
        This stores only the xT value surface, which is all you need to compute the
        xT values for new data. The value surface can be loaded back with the
        load_model function.
        
        Pickle the "ExpectedThreat" instance to store the entire model and to retain
        the transition, shot probability, move probability and scoring probability
        matrices.

        Raises
        ------
        NotFittedError
            If the model has not been fitted yet.
        ValueError
            IF the speficied output file already exists and overwrite is set to
            False.

        Parameters
        ----------
        file_path : str
            Path to file to save the surface to.
        overwrite : bool, optional
            Whether to silently overwrite any existing file at the file_path, by default True
        """
        if not np.any(self.xT):
            raise NotFittedError()
        
        if not overwrite and os.path.isfile(file_path):
            raise ValueError(
                'save_xt got overwrite=False, but a file ' 
                f"({file_path}) exists already. No data was saved."
            )
        with open(file_path, "w") as f:
            json.dump(self.xT.tolist(), f)
            
            
    def load_model(path: str) -> "ExpectedThreat":
        """Create a model from a pre-computed xT value surface.
        
        The value surface should be provided as a JSON file containing
        a 2D matrix. Karun Singh provides such a grid at the following url:
        https://karun.in/blog/data/open_xt_12x8_v1.json

        Parameters
        ----------
        path : str
            Any valid string path is acceptable.

        Returns
        -------
        ExpectedThreat
            An xT model that uses the given value surface to value actions.
        """
        grid = pd.read_json(path)
        model = ExpectedThreat()
        model.xT = grid.values
        model.w, model.l = model.xT.shape
        return model
        