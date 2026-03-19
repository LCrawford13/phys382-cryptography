import os

import numpy as np


def genBinary(bits, basis = False):
    """
    Returns a string of randomly generated zeros and ones, or plus's and x's.
    Needed for use in generating csv files for inputting real world
    experimental data. Specifically because the bases must be represented as
    +'s and x's for human use.

    Parameters
    ----------
    bits : Integer
        The number of bits or bases to be generated.
    basis : Boolean, optional
        True will turn zeros into plus's, and ones into x's.
        False will just output zeros and ones.
        The default is False.

    Returns
    -------
    temp : String
        A sequence of zeros and ones or plus's and minus's.
    """
    arr = np.random.randint(0, 2, [bits])
    result = np.array2string(arr, separator = ",",
                             max_line_width = 1e30)[1:2 * bits]

    if basis:
        result = result.replace("0", "+")
        result = result.replace("1", "x")

    return result


def createFile(bits):
    """
    Creates a csv file for demonstrating how an eavesdropper can be detected
    using quantum cryptography. Specifically, with six lines filled. The first
    with a randomly generated binary number. Three others with random sequence
    of plus's or x's, which determine a base to send or recieve a bit. And two
    empty lines for inputting experimental data into. The data can be analysed
    by the analyseFile function.

    Parameters
    ----------
    bits : Integer
        The number of bits or bases to be generated.
    """
    binaryNums = [genBinary(bits).split(",")]
    for i in range(3):
        binaryNums.append(genBinary(bits, True).split(","))
    # The first value in the list represents the message sent to create the
    # encryption key. The second, third and fourth represent Alice, Eve's and
    # Bob's randomly chosen bases respectively.

    # Creates an output directory if it doesn't already exist.
    try:
        os.mkdir("Output")
    except FileExistsError:
        pass

    # Determines a name for the output file automatically.
    num = 1
    while True:
        try:
            file = open(f"Output\\Output_{num}.csv", "x")
            break
        except FileExistsError:
            num += 1

    # Writes to the output file, so that experimental data may be inputted into
    # it.
    with file:
        file.write(f"Message,{binaryNums[0]}\n")
        file.write(f"Alice Basis,{binaryNums[1]}\n")
        file.write(f"Eve Basis,{binaryNums[2]}\n")
        file.write("Eve Output\n")
        file.write(f"Bob Basis,{binaryNums[3]}\n")
        file.write("Bob Output")

    file.close()


def analyseFile(fileName):
    """
    Analyses the data gathered using the file produced by the createFile
    function. It determines the error rate of the transmission caused by the
    eavesdropper, based on the experimental data in the file.

    Parameters
    ----------
    fileName : String
        Name of the file to analyse.

    Returns
    -------
    Float or Integer
        The error rate produced by an eavsedropper - the number of bits were
        Alice and Bob's bases match, but with differeing bits divided by the
        the number of bits were Alice and Bob's bases match. Multiplied by one
        hundred to produce a percentage value.
    """
    file = open(fileName)
    with file:
        for i in range(6):
            if i == 0:
                message = file.readline().split(",")[1:]
            elif i == 1:
                aliceBasis = file.readline().split(",")[1:]
            elif i == 4:
                bobBasis = file.readline().split(",")[1:]
            elif i == 5:
                bobOutput = file.readline().split(",")[1:]
                if len(bobOutput) == 0:
                    raise ValueError("Bob has no output data.")
            else:
                # Skips lines that aren't needed.
                next(file)

    return calcError(message, aliceBasis, bobBasis, bobOutput)


def determineMessage(message, firstBasis, secondBasis):
    """
    Determines the message recieved when an initial message is sent by someone
    using firstBasis to someone using secondBasis in the BB84 protocol.

    Parameters
    ----------
    message : List of Strings or Integers
        Contains the binary message to be sent by the user of the first basis,
        either Alice or Eve.
    firstBasis : List of Strings or Integers
        Basis used by the message sender, either Alice or Eve. It can be either
        strings with +'s and x's in it, or strings with 0's and 1's or integers
        with 0's and 1's.
    secondBasis : List of Strings or Integers
        Basis used by the message reciever, either Eve or Bob. It can be either
        strings with +'s and x's in it, or strings with 0's and 1's or integers
        with 0's and 1's.

    Returns
    -------
    output : List of Integers
        Contains the message recieved by the user of the second basis, either
        Eve or Bob.
    """
    output = []
    for i in range(len(message)):
        # Conversions to np.int32 needed to ensure consistent data types,
        # especially if the basis lists use ints rather than strings.
        if firstBasis[i] == secondBasis[i]:  # Same bases, so no change.
            output.append(np.int32(message[i]))
        else:  # Bases aren't the same, so there is a 50% chance of a 0 or 1.
            output.append(np.int32(np.random.randint(0, 2)))

    return output


def calcError(message, aliceBasis, bobBasis, bobOutput, limit = None):
    """
    Calculates the error rate as a percentage caused by the presence of an
    eavesdropper. The error rate is equal to the number of bits in bobOutput
    which don't match the corresponding bit in message, only if the
    corresponding bases in aliceBasis and bobBasis match, divided by the number
    of bases in aliceBasis and bobBasis which match. Mathematically, for a
    significant number of bits, the error rate is 25%.

    Parameters
    ----------
    message : List of Strings or Integers
        Contains the binary message sent by Alice.
    aliceBasis : List of Strings or Integers
        Basis used by Alice. It can be either strings with +'s and x's in it,
        or strings with 0's and 1's or integers with 0's and 1's.
    bobBasis : List of Strings or Integers
        Basis used by Bob. It can be either strings with +'s and x's in it,
        or strings with 0's and 1's or integers with 0's and 1's.
    bobOutput : List of Strings or Integers
        Contains the binary message recieved by Bob.
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
    # Contains the number of Alice's bases which are the same as Bob's bases.
    matchBases = 0
    # Contains the number of bits with matching bases that have different bits
    # from the initial message compared to Bob's output.
    mismatchBits = 0
    cont = True
    for j in range(len(aliceBasis)):
        if limit is not None:
            if j > limit - 1:
                cont = False
        # Needed for producing a graph which shows the trend towards 25% as
        # the number of bits increases.

        if cont:
            if aliceBasis[j] == bobBasis[j]:
                matchBases += 1
                if message[j] != bobOutput[j]:
                    mismatchBits += 1
        else:
            break

    return mismatchBits / matchBases * 100


def bb84Protocol(binaryNums, limit = None):
    """
    Performs most of the BB84 protocol, and produces the error rate. The only
    part which isn't done is the generation of the initial message and the
    three bases, which are in the binaryNums parameter.

    Parameters
    ----------
    binaryNums : List of lists of Strings or Integers.
        Should have length of 4. The first list is the binary message sent by
        Alice. The second, third and fourth are the bases of Alice, Eve and Bob
        respectively; each are represented as either strings with +'s and x's
        in it, or strings with 0's and 1's or integers with 0's and 1's.
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
    eveOutput = determineMessage(binaryNums[0], binaryNums[1], binaryNums[2])
    bobOutput = determineMessage(eveOutput, binaryNums[2], binaryNums[3])

    return calcError(binaryNums[0], binaryNums[1], binaryNums[3], bobOutput,
                     limit)


def keyBB84(message, bobBasis):
    """
    Creates an encryption key using the BB84 protocol.

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
    aliceBasis = np.random.randint(0, 2, len(message))
    output = determineMessage(message, aliceBasis, bobBasis)

    key = []
    for i in range(len(output)):
        # If Bob and Alice's bases are the same, add bit to the key.
        if aliceBasis[i] == bobBasis[i]:
            key.append(np.int32(output[i]))

    return key
