import sys
import logging

# making logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=
    [
        logging.FileHandler('encryption.log'),
        #logging.StreamHandler() only when there is a need to show the logs to the user
    ]
)

#--------------------------------------------------------
#encript_table

encrypt_table = \
    {
    "A": 56,"B": 57,"C": 58,"D": 59,"E": 40,"F": 41,
    "G": 42,"H": 43,"I": 44,"J": 45,"K": 46,"L": 47,
    "M": 48,"N": 49,"O": 60,"P": 61,"Q": 62,"R": 63,
    "S": 64,"T": 65,"U": 66,"V": 67,"W": 68,"X": 69,
    "Y": 10,"Z": 11,
    "a": 12,"b": 13,"c": 14,"d": 15,"e": 16,"f": 17,
    "g": 18,"h": 19,"i": 30,"j": 31,"k": 32,"l": 33,
    "m": 34,"n": 35,"o": 36,"p": 37,"q": 38,"r": 39,
    "s": 90,"t": 91,"u": 92,"v": 93,"w": 94,"x": 95,
    "y": 96,"z": 97,
    " ": 98,",": 99, ".": 100, "'": 101,"!": 102,"-": 103,
    }





#-----------------------------------------------------------
#decfrypt_table

decrypt_table = \
    {
    56: "A", 57: "B", 58: "C", 59: "D", 40: "E", 41: "F",
    42: "G", 43: "H", 44: "I", 45: "J", 46: "K", 47: "L",
    48: "M", 49: "N", 60: "O", 61: "P", 62: "Q", 63: "R",
    64: "S", 65: "T", 66: "U", 67: "V", 68: "W", 69: "X",
    10: "Y", 11: "Z",
    12: "a", 13: "b", 14: "c", 15: "d", 16: "e", 17: "f",
    18: "g", 19: "h" ,30: "i", 31: "j", 32: "k", 33: "l",
    34: "m", 35: "n", 36: "o", 37: "p", 38: "q", 39: "r",
    90: "s", 91: "t", 92: "u", 93: "v", 94: "w", 95: "x",
    96: "y", 97: "z",
    98: " ", 99: ",", 100: ".", 101: "'", 102: "!", 103: "-",
}




#---------------------------------------------------------------------------------
def convert (): #-> string
    """
    The def converts the string input to a list of the numbers that are keyed to each letter in the encrypt dictionary  in a form of string,
    then joins that list and returns it.
    """
    word = input ('write a world to encrypt')
    logging.info(f"Starting encryption process for text of length {len(word)}")
    result_nums = [] #creating empty list
    # ---------------------------------------------------------------------------------
    if len(word) == 0:  # checks if the input is empty then returns am empty list if true
        return result_nums
    # ---------------------------------------------------------------------------------
    for char in word: #gives the num keyed to each letter
        try:
           num = encrypt_table[char]
           result_nums.append(str(num))
        except KeyError as char1: #if the user has entered a letter that is not in the encryption table + logging as an error and then raise to stop running
           logging.error(f"Character '{char1}' not found in encryption table")
           print ('your word has a letter that is not in the encryption table')
           raise
    result_nums = ','.join(result_nums)
    logging.info("Encryption completed successfully")
    return result_nums




#---------------------------------------------------------------------------------

def convert_backwords (decrypt1_nums): #-> string
    """
      The def converts back a list of numbers to a list of strings that are keyed to each number in the decrypt dictionary,
      joins that list and then returns it.
      """
    logging.info("Starting decryption process")
    parts = decrypt1_nums.split(",")
    # ------------------------------------
    if  len(parts) == 1 and parts[0] == "": #checks if the file is empty then returns empty brackets if true
        return parts[0]                     #  (==1) because even when the list is empty it still counts it as one variable
    # ------------------------------------
    result_chars = [] #creats an empty list
    decrypt1_nums = decrypt1_nums.split(",") #splits the file content into a list
    for num_str in decrypt1_nums:# converts the nums into the letters that are keyed to them then puts it in a new list
        try:
           char = decrypt_table[int(num_str)]
           result_chars.append(char)
        except (KeyError, ValueError) as z: #if one of the values of the file does not exist in the dictionary then +logging error
           logging.error(f"Failed to decrypt value '{num_str}': {z}")
           raise
    logging.info("Decryption completed successfully")
    return ''.join(result_chars)





#---------------------------------------------------------------------------------
def main_encrypt(encrypted_word):
   """
      this function only writes the encrypted message that "convert" created onto a file and also has a log that
       informs if it was successful or not.


   """
   logging.info("Encrypt mode activated")
   try:
         with open("origin_file", "w") as file1:
            (file1.write(encrypted_word)) # writes the encrypted letters to the origin file
         logging.info("Encrypted data written to origin_file successfully")
   except Exception as t: #if the user has entered a massage that is not valid
         logging.error(f"Failed to write encrypted data: {t}")


# ---------------------------------------------------------------------------------
def main_decrypt():
    """
    this function reads from the existing file then calls the convert backwords function in order to
    convert the file back using yhe decryption table, and then it prints the decrypted massage.
    excepts are for invalid cc in the file, and if the file hasn't been found or hasn't been created

    """
    logging.info("Decrypt mode activated")
    try:
        with open("origin_file", "r") as file:
            decrypt_nums = file.read()
        logging.info("Encrypted data read from origin_file successfully")
        print(convert_backwords(decrypt_nums))
    except FileNotFoundError:
        logging.error("origin_file not found")
        print("file hasn't been created yet")
        raise
    except Exception as e:
        logging.error(f"Failed to decrypt: {e}")
        raise







#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------

if __name__== "__main__":
    #assers check
    check1 = 'abcdefghijklmnopqrstuvwxyz !,-'
    check2 = 'ABCDEFGHIJKLMNOPQRSTUVWXY'
    for char in check1:
        assert decrypt_table[encrypt_table[char]] == char, "Code error :The encrypt table and the decrypt table are not synchronized"

    # Test uppercase
    for char in check2:
        assert decrypt_table[encrypt_table[char]] == char, "Code error :The encrypt table and the decrypt table are not synchronized"
    print ("The encrypt table and the decrypt table were synchronized successfully!")

    if sys.argv[1] == 'encrypt': #checks sys.argv[1]
        result_nums = convert()
        main_encrypt(result_nums)

    elif sys.argv[1] == 'decrypt': #checks sys.argv[1]
        main_decrypt()

    else: #if the two ifs (if and elif) are false then user must have entered a wrong sys.argv[1] therefor we have a logging error and a print to the user
        logging.error("sys.argv has been failed to be read")
        print ('sys.argv variable is incorrect please check it')







