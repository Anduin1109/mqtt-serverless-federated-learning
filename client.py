from typing import Dict

import torch

import config
from utils import logger
import mqtt
from tqdm import tqdm
from time import sleep
from sklearn.metrics import accuracy_score, roc_auc_score


def map_at_k(output, target, k) -> float:
    _, predicted = output.topk(k, 1, True, True)
    predicted = predicted.t()
    correct = predicted.eq(target.view(1, -1).expand_as(predicted))
    correct = correct[:k].reshape(-1).float().sum(0, keepdim=True)
    map_10 = correct.mul_(100.0 / config.BATCH_SIZE)
    return map_10.item()


# a client that holds the model, dataset, and mqtt client
class Client:
    def __init__(
            self, net, optimizer, criterion, logger,
            device: str = "cpu",
    ):
        self.logger = logger
        self.model = net.to(device)
        self.criterion = criterion
        self.optimizer = optimizer(self.model.parameters(), lr=config.LEARNING_RATE)

        self.mqtt = mqtt.MQTTClient()

    def get_params(self):
        return self.model.state_dict()

    def train(self, train_loader):
        #self.logger.info("training...")
        #self.logger.info(f'Epoch {i + 1}/{config.EPOCHS}')
        for data, target in train_loader:
            data, target = data.to(config.DEVICE), target.to(config.DEVICE)
            self.model.zero_grad()
            output = self.model(data)
            loss = self.criterion(output, target)
            loss.backward()
            self.optimizer.step()

    def validate(self, val_loader, k: int = 5) -> Dict[str, float]:
        """
        Validate the model
        :param k: map@k accuracy
        :param val_loader:
        :return: average losses
        """
        losses = []
        accs = []
        for data, target in val_loader:
            data, target = data.to(config.DEVICE), target.to(config.DEVICE)
            output = self.model(data)
            # loss
            loss = self.criterion(output, target)
            losses.append(loss.item())
            # accuracy@k
            acc = map_at_k(output, target, k)
            accs.append(acc)

        return {
            "loss": sum(losses) / len(losses),
            "map@k": sum(accs) / len(accs),
        }

    def test(self, test_loader, k: int = 5) -> Dict[str, float]:
        losses = []
        accs = []
        for data, target in test_loader:
            data, target = data.to(config.DEVICE), target.to(config.DEVICE)
            output = self.model(data)
            # loss
            loss = self.criterion(output, target)
            losses.append(loss.item())
            # accuracy@k
            acc = map_at_k(output, target, k)
            accs.append(acc)

        return {
            "loss": sum(losses) / len(losses),
            "map@k": sum(accs) / len(accs),
        }

    def start_communicate(self):
        sleep(0.7)

    def save_model(self, dir_path: str = './checkpoints/'):
        sleep(0.7)
