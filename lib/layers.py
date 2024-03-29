import tensorflow as tf

xavier_initializer = tf.contrib.layers.xavier_initializer



def add_softmax(name, out, out_size):
    with tf.variable_scope(name):
        in_size = out.shape[-1]
        W = tf.get_variable('W', [in_size, out_size],
                            initializer=xavier_initializer())
        b = tf.get_variable('b', [out_size],
                            initializer=tf.zeros_initializer())
        logits = tf.matmul(out, W) + b

        probs = tf.nn.softmax(logits)
    return logits, probs


def add_conv1d(name, inputs, width, out_channels):
    conv_filter = tf.get_variable(name, [width, inputs.shape[2], out_channels],
                                  initializer=xavier_initializer())
    return tf.nn.conv1d(inputs, conv_filter, 1, 'SAME')


def add_conv3f(name, out, windows, out_channels, dp):
    with tf.variable_scope(name):
        outs = []
        for w in windows:
            outs.append(add_conv1d('f' + str(w), out, w, out_channels))
        out = tf.concat(outs, -1)
        out = tf.layers.batch_normalization(out)
        out = tf.nn.relu(out)
        out = tf.layers.dropout(out, dp)
    return out


def add_embedding(inputs, vocab_size, hidden_size, dropout):
    """
        @config:
        @inputs:        (tf.int32)    seq_len x batch_size
        @vocab_size:    (tf.int32)
        @hidden_size:   (tf.int32)
        @dropout:       (tf.float32)  scalar
        @return:
            outputs:    (tf.float32)  seq_len x batch_size x hidden_size
    """
    with tf.variable_scope('EncodingEmbedding'):
        w2v = tf.get_variable('w2v',
                              [vocab_size, hidden_size],
                              initializer=xavier_initializer())
        outputs = tf.nn.embedding_lookup(params=w2v, ids=inputs)
        outputs = tf.nn.dropout(outputs, rate= 1- dropout)
    return outputs
