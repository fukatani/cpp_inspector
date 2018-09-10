//#include <memory>
// #include <stdio.h>

class Object {
 public:
  int FuncU();
  int cc_ = 0;
 private:
  int dd_ = 0;
  int ee = 0;
};

int DekkaiFunc(int a, const double c, const double& d, double* out) {
  return 2;
}

void Get(double* out) {
  &out = 2;
}

int global_var = 9;

int main() {
  const int a = 1;
  double c = (double)2.2;
  c = c + 1;
  Get(&c);
  for (int i = 0; i < 3; i++) {
  }
  for (int i = 0; i < 3; ++i) {
  }
  int n = NULL;
  int nn = nullptr;
  int at = sizeof(a);
  int bt = sizeof(int);
  constexpr int con = 9;
  int cong = 9;

  int *p1;
  p1 = new int(10);  

  std::unique_ptr<int> p2;
  p2.reset(new int(10));
}
