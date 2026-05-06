# Quick logic check for  Mano Machine script
n = 11
k = 7
sum_val = 0

for i in range(1, n + 1):
    temp = i
    # This simulates repeated subtraction logic
    while temp >= k:
        temp -= k
    
    if temp == 0:
        sum_val += i
        print(f"Multiple found: {i}")

print(f"Final Sum: {sum_val}")
print(f"Hex Equivalent: {hex(sum_val)}")