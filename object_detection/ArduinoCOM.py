import serial
import time


startMarker = 60
endMarker = 62

def sendToArduino(ser, sendStr):
  ser.write(bytes(sendStr, "UTF-8"))


def recvFromArduino(ser):
  global startMarker, endMarker

  ck = ""
  x = "z" # any value that is not an end- or startMarker
  byteCount = -1 # to allow for the fact that the last increment will be one too many

  # wait for the start character
  while  ord(x) != startMarker:
    x = ser.read()

  # save data until the end marker is found
  while ord(x) != endMarker:
    if ord(x) != startMarker:
      ck = ck + x.decode("UTF-8")
      byteCount += 1
    x = ser.read()

  return(ck)


def waitForArduino(ser):

   # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
   # it also ensures that any bytes left over from a previous message are discarded

    global startMarker, endMarker

    msg = ""
    while msg.find("Arduino is ready") == -1:

      while ser.inWaiting() == 0:
        pass

      msg = recvFromArduino()

      print(msg)
      print()

#======================================

def runTest(ser, td):
  numLoops = len(td)
  waitingForReply = False

  n = 0
  while n < numLoops:

    teststr = td[n]

    if waitingForReply == False:
      sendToArduino(ser, teststr)
      print("Sent from PC -- LOOP NUM " + str(n) + " TEST STR " + teststr)
      waitingForReply = True

    if waitingForReply == True:

      while ser.inWaiting() == 0:
        pass

      dataRecvd = recvFromArduino(ser)
      print("Reply Received  " + dataRecvd)
      n += 1
      waitingForReply = False

      print("===========")

    time.sleep(5)





# NOTE the user must ensure that the serial port and baudrate are correct


