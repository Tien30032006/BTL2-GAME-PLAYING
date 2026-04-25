from Co_ganh import main2

def run_test(n):
    win_X = 0
    win_O = 0
    draw = 0

    for i in range(n):
        print(f"\n===== GAME {i+1} =====")
        result = main2('X')  # X đi trước

        if result == 1:
            print("➡ X thắng")
            win_X += 1
        elif result == -1:
            print("➡ O thắng")
            win_O += 1
        else:
            print("➡ Hòa")
            draw += 1

    print("\n===== RESULT =====")
    print(f"X thắng: {win_X}")
    print(f"O thắng: {win_O}")
    print(f"Hòa   : {draw}")


if __name__ == "__main__":
    run_test(100)