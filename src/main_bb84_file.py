import bb84

process = input("Input 0 to generate file, input 1 to analyse file.")
if process == "0":
    bits = input("Input the number of bits.")
    bb84.createFile(int(bits))
elif process == "1":
    num = input("Input file number to be analysed.")
    errorRate = bb84.analyseFile(f"Output\\Output_{num}.csv")
    print(f"Error Rate: {errorRate:.4f}%")
