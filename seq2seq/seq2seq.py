import keras
from keras.models import Sequential
from keras.layers.core import Dense

from lstm_encoder import LSTMEncoder
from lstm_decoder import LSTMDecoder, LSTMDecoder2
from stateful_container import StatefulContainer

class Seq2seq(StatefulContainer):
	def __init__(self, output_dim, hidden_dim,output_length, init='glorot_uniform', inner_init='orthogonal', forget_bias_init='one', activation='tanh', inner_activation='hard_sigmoid',
                 weights=None, truncate_gradient=-1,
                 input_dim=None, input_length=None, hidden_state=None, batch_size=None, depth=1, remember_state=False,
                 ):

		if not type(depth) == list:
			depth = [depth, depth]
		n_lstms = sum(depth)

		if weights is None:
			weights = [None] * (n_lstms + 1)

		if hidden_state is None:
			hidden_state = [None] * (n_lstms + 1)

		encoder_index = depth[0] - 1
		decoder_index = depth[0] + 1

		decoder = LSTMDecoder(dim=output_dim, hidden_dim=hidden_dim, output_length=output_length,
							  init=init,inner_init=inner_init, activation=activation, 
							  inner_activation=inner_activation,weights=weights[decoder_index],
							  truncate_gradient = truncate_gradient, 
							  hidden_state=hidden_state[decoder_index], batch_size=batch_size, remember_state=remember_state)

		encoder = LSTMEncoder(input_dim=input_dim, output_dim=hidden_dim,init=init,
							  inner_init=inner_init, activation=activation, 
							  inner_activation=inner_activation,weights=weights[encoder_index],
							  truncate_gradient = truncate_gradient, input_length=input_length,
							  hidden_state=hidden_state[encoder_index], batch_size=batch_size, remember_state=remember_state)

		left_deep = [LSTMEncoder(input_dim=input_dim, output_dim=input_dim,init=init,
							  inner_init=inner_init, activation=activation, 
							  inner_activation=inner_activation,weights=weights[i],
							  truncate_gradient = truncate_gradient, input_length=input_length,
							  hidden_state=hidden_state[i], batch_size=batch_size, return_sequences=True, remember_state=remember_state)
					for i in range(depth[0]-1)]


		right_deep = [LSTMEncoder(input_dim=output_dim, output_dim=output_dim,init=init,
							  inner_init=inner_init, activation=activation, 
							  inner_activation=inner_activation,weights=weights[decoder_index + 1 + i],
							  truncate_gradient = truncate_gradient, input_length=input_length,
							  hidden_state=hidden_state[decoder_index + 1 + i], batch_size=batch_size, return_sequences=True, remember_state=remember_state)
					for i in range(depth[1]-1)]

		dense = Dense(input_dim=hidden_dim, output_dim=output_dim)
		encoder.broadcast_state(decoder)
		if weights[depth[0]] is not None:
			dense.set_weights(weights[depth[0]])
		super(Seq2seq, self).__init__()
		for l in left_deep:
			self.add(l)
		self.add(encoder)
		self.add(dense)
		self.add(decoder)
		for l in right_deep:
			self.add(l)
		self.encoder = encoder
		self.dense = dense
		self.decoder = decoder
		self.left_deep = left_deep
		self.right_deep = right_deep
