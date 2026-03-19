import numpy as np

import bb84


def senderBasis(message):
    """
    Creates Alice's basis based off of the message to be sent by Alice.

    Parameters
    ----------
    message : List of Strings or Integers
        Contains the binary message to be sent by Alice.

    Returns
    -------
    basis : List of Strings or Integers
        Contains the basis used by Alice.
    """
    basis = np.empty((len(message)), dtype = np.int32)
    for x in range(len(message)):
        # If the message bit is zero, Alice uses + basis, and vice versa.
        if message[x] == 0:
            basis[x] = 1
        elif message[x] == 1:
            basis[x] = 0

    return basis


def b92Protocol(binaryNums, limit = None):
    """
    Performs most of the B92 protocol in the presence of an eavesdropper, and
    produces the error rate. It requires an initial message, and Eve and Bob's
    bases.

    Parameters
    ----------
    binaryNums : List of lists of Strings or Integers.
        Should have length of 3. The first list is the binary message sent by
        Alice. The second and third is Eve's and Bob's bases respectively; each
        are represented as either strings with +'s and x's in it, or strings
        with 0's and 1's or integers with 0's and 1's.
    limit : Integer, optional
        Determines the maximum number of bits to include in the calculation of
        the error rate. For example, if the message is 50 bits long, but the
        limit is 30, then only the first 30 bits will be included in the
        calculation. The default is None, which means that there is no limit.

    Returns
    -------
    Float
        The error rate of mismatching bits as a percentage caused by the
        presence of an eavesdropper.
    """
    aliceBasis = senderBasis(binaryNums[0])
    eveOutput = bb84.determineMessage(binaryNums[0], aliceBasis, binaryNums[1])
    bobOutput = bb84.determineMessage(eveOutput, binaryNums[1], binaryNums[2])

    return bb84.calcError(binaryNums[0], aliceBasis, binaryNums[2],
                          bobOutput, limit)


def keyB92(message, bobBasis):
    """
    Creates an encryption key using the B92 protocol.

    Parameters
    ----------
    message : List of Strings or Integers
        Contains the binary message sent by Alice.
    bobBasis : List of Strings or Integers
        Basis used by Bob. It can be either strings with +'s and x's in it,
        or strings with 0's and 1's or integers with 0's and 1's.

    Returns
    -------
    key : List of Integers or Floats
        An encryption key.
    """
    aliceBasis = senderBasis(message)
    output = bb84.determineMessage(message, aliceBasis, bobBasis)

    key = []
    for i in range(len(output)):
        # If Bob recieves a 0 in the + basis or he recieves a 1 in the x basis,
        # add the bit to the key.
        if ((bobBasis[i] == 0 and output[i] == 0) or
           (bobBasis[i] == 1 and output[i] == 1)):
            key.append(np.int32(output[i]))

    return key
