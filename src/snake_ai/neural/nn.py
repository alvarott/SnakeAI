# This module contains the implementation of the neural network that will act as Snake brain

# Author: Álvaro Torralba
# Date: 16/05/2023
# Version: 0.0.1

from snake_ai.neural.nn_functions import NNFunctionFactory
import numpy as np


class NN:
    """
    This class provides the functionality necessary to act as a brain of the snake, with a simple implementation of
    a neural network, is not intended to provide a full implementation of a NN capacities
    """

    # Class constants
    W_NAME = 'layer_'
    B_NAME = 'bias_'

    def __init__(self, input: int, output: int, hidden: list[int], output_init: str, bias: bool,
                 hidden_init: str, output_act: str, hidden_act: str, bias_init: str = 'zero'):
        """
        Constructor
        :param input: input nodes to the NN
        :param output: output nodes from the NN
        :param hidden: list with the number of nodes of each hidden layer
        :param output_init: output layer weights initialization method to be used
        :param bias: flag to introduce or not bias vector
        :param bias_init: bias initialization method to be used
        :param hidden_init: hidden layers initialization method to be used
        :param output_act: output layer activation function
        :param hidden_act: hidden layers activation function
        """
        if input < 1 or output < 1:
            raise ValueError(f"Input and output layer must contain at least 1 node. Found: (input_nodes:{input},"
                             f" output_nodes:{output})")
        elif output_init == 'zero' or hidden_init == 'zero':
            raise ValueError(f'Zero is not a supported initialization for output or hidden layers')
        elif not isinstance(hidden, list):
            raise ValueError(f"Expected type for hidden param: {type(list())}. Found: {type(hidden)} ")

        self._func_factory = NNFunctionFactory()
        self._input = input
        self._output = output
        self._output_init = self._func_factory.get_function('initialization', output_init)
        self._output_act = self._func_factory.get_function('activation', output_act)
        self._hidden = hidden
        self._hidden_init = self._func_factory.get_function('initialization', hidden_init)
        self._hidden_act = self._func_factory.get_function('activation', hidden_act)
        self._bias = bias
        self._bias_init = self._func_factory.get_function('initialization', bias_init)
        self._bias_vec = {}
        self._w_matrices = {}
        self._activations = {}
        self._codification_info: dict[str, int | list[int]] = {}
        self._dense_initialization()
        self._set_codification()

    def __str__(self):
        return f'Inputs nodes  :  {self._input}\n' \
               f'Outputs nodes :  {self._output}\n' \
               f'Hidden nodes  :  {self._hidden}\n'\
               f'Bias          :  {self._bias}\n'\
               f'Output init   :  {self._output_init.__name__}\n' \
               f'Hidden init   :  {self._hidden_init.__name__}\n' \
               f'Bias init     :  {self._bias_init.__name__}\n'\
               f'Output act    :  {self._output_act.__name__}\n'\
               f'Hidden act    :  {self._hidden_act.__name__}\n'

    @property
    def layers(self):
        layers = list(self._hidden)
        layers.insert(0, self._input)
        layers.append(self._output)
        return layers

    @property
    def activations(self) -> dict[int, list[float]]:
        """
        Holds the last forward propagation outputs
        :return:
        """
        return self._activations

    def _set_codification(self) -> None:
        """
        Produces the codification additional information for the weights and biases
        :return:
        """
        # Calculate length of the encoding array
        length = 0
        values = list(self._w_matrices.values())
        biases = list(self._bias_vec.values())
        slices = []
        for i in range(len(values)):
            slice = values[i].size
            length += slice
            slices.append(slice)
            if self._bias:
                slice = biases[i].size
                length += slice
                slices.append(slice)
        self._codification_info['length'] = length
        self._codification_info['slices'] = slices

    def _dense_initialization(self) -> None:
        """
        Produces a dense initialization of the NN
        :return:
        """
        nodes = list([self._input, *self._hidden, self._output])
        weights = {}
        bias = {}

        # For every layer of connections
        for i in range(len(nodes) - 1):
            # If output layer
            if i + 2 == len(nodes):
                weights[f'{NN.W_NAME}{i}'] = self._output_init((nodes[i + 1], nodes[i]))
            # If hidden layer
            else:
                weights[f'{NN.W_NAME}{i}'] = self._hidden_init((nodes[i + 1], nodes[i]))
            # Bias
            if self._bias:
                bias[f'{NN.B_NAME}{i}'] = self._bias_init((nodes[i + 1], 1))

        self._w_matrices = weights
        self._bias_vec = bias

    def forward_prop(self, input: np.ndarray) -> np.ndarray:
        """
        Forward propagation of the NN function
        :param input: and array with the input to the NN just support 1D-arrays or one column matrices
        :return output, activations: the response of the NN to the input, and the dict with the outputs of each layer
        """
        # Reject any invalid input
        if input.ndim > 2 or (input.ndim == 2 and (input.shape[0] > 1 and input.shape[1] > 1)):
            raise ValueError("No supported input to the NN. Supported inputs: [1-D arrays or one (row|col) matrices]")
        # Transpose to columnar format
        elif input.ndim == 2:
            if input.shape[1] > 1:
                _input = input.T
            else:
                _input = input
        # If 1D-array reshape to one column matrix
        elif input.ndim == 1:
            _input = input.reshape(-1, 1)
        else:
            return np.empty(0)

        activations = {}
        output: np.ndarray = np.empty(0)
        for i in range(len(self._w_matrices)):
            if i == 0:
                output = np.matmul(self._w_matrices[f'{NN.W_NAME}{i}'], _input)
            else:
                output = np.matmul(self._w_matrices[f'{NN.W_NAME}{i}'], output)
            if self._bias:
                output = output + self._bias_vec[f'{NN.B_NAME}{i}']
            if i == len(self._w_matrices) - 1:
                output = self._output_act(output)
            else:
                output = self._hidden_act(output)
            activations[i] = list(output.copy().flatten())
        self._activations = activations
        return output.flatten()

    def encode(self) -> np.ndarray:
        """
        Produces a 1D-array encoding of all weight and biases
        :return:
        """
        encoding = np.empty(0)
        matrices = list(self._w_matrices.values())
        biases = list(self._bias_vec.values())
        for i in range(len(matrices)):
            encoding = np.concatenate((encoding, matrices[i].flatten()))
            if self._bias:
                encoding = np.concatenate((encoding, biases[i].flatten()))
        return encoding

    def decode(self, nn_code: np.ndarray) -> None:
        old_w = list(self._w_matrices.values())
        old_b = list(self._bias_vec.values())
        slices = self._codification_info['slices']
        length = self._codification_info['length']
        slice_count = 0
        count = 0
        if nn_code.ndim > 1:
            raise ValueError("Just 1D-arrays are supported as NN codification")
        if len(nn_code) != length:
            raise ValueError(f"Wrong encoding array for this NN expected length={length}"
                             f".Found: 'len(nn_code)'={len(nn_code)}")

        for i in range(len(old_w)):
            self._w_matrices[f'{NN.W_NAME}{i}'] = nn_code[slice_count:slice_count + slices[count]].reshape(old_w[i].shape)
            slice_count += slices[count]
            count += 1
            if self._bias:
                self._bias_vec[f'{NN.B_NAME}{i}'] = nn_code[slice_count:slice_count + slices[count]].reshape(old_b[i].shape)
                slice_count += slices[count]
                count += 1
