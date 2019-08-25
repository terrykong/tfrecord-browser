TFRecord Browser
===
A simple command line utility to browse trecord binary files. I was motivated by the lack of support for reading this file
format. Normally one would have to write a one-off python script to read through your file. This project aims to reduce
the lines of code you need to write.

![Usage](demo/usage.gif)

Prerequisites
===
This project doesn't install tensorflow, rather it assumes it's already there since you may have the cpu or gpu version installed
and this project doesn't require one over the other. In an effort to align with the mission of moving to TF 2.0, this project
will use eager syntax so it is recommended to use 2.0
```
# CPU
pip install tensorflow==2.0.0-rc0
# GPU
pip install tensorflow-gpu==2.0.0-rc0
```

Installation
===
```
pip install git+https://github.com/terrykong/tfrecord-browser
```

Usage
===
```
tfrecord-browser <tfrecord_path>
```

TODOs
===
+ Add support for searching
+ Add support for skipping/jumping
+ Add to PyPi
+ Currently only supports tf.train.Example, but need to also support for tf.train.SequenceExample
