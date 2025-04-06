def get_reversed_num(num):
  reversed_num = 0 
  while num != 0:
    current_digit = num % 10
    reversed_num = reversed_num * 10 + current_digit
    num = num // 10
  
  return reversed_num
  
  
num = int(input())
get_reversed_num(num)
#for i in range(tc_count):
  #num = int(input())
  #print(get_reversed_num(num))