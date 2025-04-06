#include <iostream>
using namespace std;

int getReversedNum(int num) {
    int reversedNum = 0;
    while (num != 0) {
        int currentDigit = num % 10;
        reversedNum = reversedNum * 10 + currentDigit;
        num = num / 10;
    }
    return reversedNum;
}

int main() {
    int tcCount;
    cin >> tcCount;
    cout << getReversedNum(tcCount) << endl;
    return 0;
}
