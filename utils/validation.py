import tqdm
import torch
import torch.nn as nn
import torch.nn.functional as F

from .gmm import sample_gmm


def validate(args, model, melgen, tierutil, testloader, criterion, writer, step):
    model.eval()
    torch.backends.cudnn.benchmark = False

    test_loss = []
    loader = tqdm.tqdm(testloader, desc='Testing is in progress')
    with torch.no_grad():
        for input_tuple in loader:
            if args.tts:
                seq, input_lengths, source, target = input_tuple
                mu, std, pi, alignment = model(source.cuda(non_blocking=True),
                                                seq.cuda(non_blocking=True),
                                                input_lengths.cuda(non_blocking=True))
            else:
                source, target = input_tuple
                mu, std, pi = model(source.cuda(non_blocking=True))
            loss = criterion(target.cuda(non_blocking=True), mu, std, pi)
            test_loss.append(loss)

        test_loss = sum(test_loss) / len(test_loss)
        source = source[0].cpu().detach().numpy()
        target = target[0].cpu().detach().numpy()
        alignment = alignment[0].cpu().detach().numpy()
        result = sample_gmm(mu[0], std[0], pi[0]).cpu().detach().numpy()
        writer.log_validation(test_loss, source, target, result, alignment, step)

    model.train()
    torch.backends.cudnn.benchmark = True
