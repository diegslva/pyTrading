# Deep LSTM with hidden state forwarding
import keras
from keras.models import Sequential
from keras.layers.core import RepeatVector

from seq2seq.lstm_encoder import LSTMEncoder as lstm
from seq2seq.stateful_container import StatefulContainer

class DeepLSTM(StatefulContainer):
    def __init__(self, input_dim, output_dim, depth=2,
                 init='glorot_uniform', inner_init='orthogonal', forget_bias_init='one',
                 activation='tanh', inner_activation='hard_sigmoid',
                 weights=None, truncate_gradient=-1, input_length=None, hidden_state=None, batch_size=None, return_sequences = False, inner_return_sequences = False, remember_state=False,go_backwards=False, **kwargs):
        nlayer = depth
        self.state = []
        if depth < 1:
            raise Exception("Minimum depth is 1")
        if depth > 1 and inner_return_sequences:
            nlayer = depth*2 - 1
        if weights is None:
            weights = [None]*nlayer
        if hidden_state is None:
            hidden_state = [None]*nlayer

        super(DeepLSTM, self).__init__()
        def get_lstm(idim, odim, rs, reverse=False):
            return lstm(input_dim=idim, output_dim=odim, init=init,
                    inner_init=inner_init, forget_bias_init=forget_bias_init,
                    activation=activation, inner_activation=inner_activation,
                    weights=weights[len(self.layers)], truncate_gradient=truncate_gradient,
                    input_length=input_length, hidden_state=hidden_state[len(self.layers)],
                    batch_size=batch_size, return_sequences=rs,
                    remember_state=remember_state, go_backwards=reverse, **kwargs)
        if depth == 1:
            self.add(get_lstm(input_dim, output_dim, return_sequences))
        else:
            lstms = []

            layer = get_lstm(input_dim, output_dim, inner_return_sequences, go_backwards)
            lstms.append(layer)
            self.add(layer)
            if not inner_return_sequences:
                self.add(RepeatVector(input_length))

            for i in range(depth-2):
                layer = get_lstm(output_dim, output_dim, inner_return_sequences)
                lstms.append(layer)
                self.add(layer)
                if not inner_return_sequences:
                    self.add(RepeatVector(input_length))

            layer = get_lstm(output_dim, output_dim, return_sequences)
            lstms.append(layer)
            self.add(layer)     

            for i in range(len(lstms)-1):#connect hidden layers.
                lstms[i].broadcast_state(lstms[i+1])
