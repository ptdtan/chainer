from unittest import TestCase
import numpy
from chainer      import cuda, Variable
from chainer.cuda import to_cpu, to_gpu, GPUArray
from chainer.gradient_check import assert_allclose, numerical_grad
from chainer.functions import average_pooling_2d, max_pooling_2d

cuda.init()

class TestMaxPooling2D(TestCase):
    def setUp(self):
        self.x  = numpy.random.uniform(-1, 1, (2, 3, 4, 3)).astype(numpy.float32)
        self.gy = numpy.random.uniform(-1, 1, (2, 3, 2, 2)).astype(numpy.float32)

    def check_forward(self, x_data, use_cudnn=True):
        x = Variable(x_data)
        y = max_pooling_2d(x, 3, stride=2, pad=1, use_cudnn=use_cudnn)
        if isinstance(y.data, GPUArray):
            y_data = y.data.get()
        else:
            y_data = y.data

        self.assertEqual((2, 3, 2, 2), y_data.shape)
        for k in xrange(2):
            for c in xrange(3):
                expect = numpy.array([
                    [self.x[k, c, 0:2, 0:2].max(), self.x[k, c, 0:2, 1:3].max()],
                    [self.x[k, c, 1:4, 0:2].max(), self.x[k, c, 1:4, 1:3].max()]])
                assert_allclose(expect, y_data[k, c])

    def test_forward_cpu(self):
        self.check_forward(self.x)

    def test_forward_gpu(self):
        self.check_forward(to_gpu(self.x))

    def test_forward_gpu_no_cudnn(self):
        self.check_forward(to_gpu(self.x), False)

    def check_backward(self, x_data, y_grad, use_cudnn=True):
        x = Variable(x_data)
        y = max_pooling_2d(x, 3, stride=2, pad=1, use_cudnn=use_cudnn)
        y.grad = y_grad
        y.backward()

        func = y.creator
        f = lambda: func.forward((x.data,))
        gx, = numerical_grad(f, (x.data,), (y.grad,))

        assert_allclose(to_cpu(gx), to_cpu(x.grad))

    def test_backward_cpu(self):
        self.check_backward(self.x, self.gy)

    def test_backward_gpu(self):
        self.check_backward(to_gpu(self.x), to_gpu(self.gy))

    def test_backward_gpu_no_cudnn(self):
        self.check_backward(to_gpu(self.x), to_gpu(self.gy), False)


class TestAveragePooling2D(TestCase):
    def setUp(self):
        self.x  = numpy.random.uniform(-1, 1, (2, 3, 4, 3)).astype(numpy.float32)
        self.gy = numpy.random.uniform(-1, 1, (2, 3, 2, 2)).astype(numpy.float32)

    def check_forward(self, x_data, use_cudnn=True):
        x = Variable(x_data)
        y = average_pooling_2d(x, 3, stride=2, pad=1, use_cudnn=use_cudnn)
        if type(y.data) == GPUArray:
            y_data = y.data.get()
        else:
            y_data = y.data

        self.assertEqual((2, 3, 2, 2), y_data.shape)
        for k in xrange(2):
            for c in xrange(3):
                expect = numpy.array([
                    [self.x[k, c, 0:2, 0:2].sum(), self.x[k, c, 0:2, 1:3].sum()],
                    [self.x[k, c, 1:4, 0:2].sum(), self.x[k, c, 1:4, 1:3].sum()]]
                ) / 9
                assert_allclose(expect, y_data[k, c])

    def test_forward_cpu(self):
        self.check_forward(self.x)

    def test_forward_gpu(self):
        self.check_forward(to_gpu(self.x))

    def test_forward_gpu_no_cudnn(self):
        self.check_forward(to_gpu(self.x), False)

    def check_backward(self, x_data, y_grad, use_cudnn=True):
        x = Variable(x_data)
        y = average_pooling_2d(x, 3, stride=2, pad=1, use_cudnn=use_cudnn)
        y.grad = y_grad
        y.backward()

        func = y.creator
        f = lambda: func.forward((x.data,))
        gx, = numerical_grad(f, (x.data,), (y.grad,), eps=1e-2)

        assert_allclose(to_cpu(gx), to_cpu(x.grad))

    def test_backward_cpu(self):
        self.check_backward(self.x, self.gy)

    def test_backward_gpu(self):
        self.check_backward(to_gpu(self.x), to_gpu(self.gy))

    def test_backward_gpu_no_cudnn(self):
        self.check_backward(to_gpu(self.x), to_gpu(self.gy), False)