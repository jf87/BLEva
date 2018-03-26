# BLEva: Evaluating Bluetooth Low Energy for IoT

BLEva is a benchmarking framework for Bluetooth Low Energy applications.

## Folder Structure

- `./src/bleva-android`: Android application code.
- `.src/bled112`: [BLED112 (CC2540)](https://www.silabs.com/products/wireless/bluetooth/bluetooth-low-energy-modules/bled112-bluetooth-smart-dongle) code.
- `./src/bleva-server`: Server code to coordinate Android and BLED112 processes.
- `./CPSBench`: Benchmark configs, results and plotting scripts of [CPSBench paper](https://cpsbench2018.ethz.ch/).

## Citation
Please cite the following paper if you use this code in any ways:

```
@inproceedings{fuerst2018bleva,
  title={Evaluating Bluetooth Low Energy for IoT},
  author={F{\"u}rst, Jonathan and Chen, Kaifei and Kim, Hyung-Sin and Bonnet, Philippe},
  booktitle={Proceedings of the 1st Workshop on Benchmarking Cyber-Physical Networks and Systems},
  year={2018},
  organization={ACM/IEEE}
}
```

## Contact
Please email Jonathan Fürst <jonf@itu.dk>.
