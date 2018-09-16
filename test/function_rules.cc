class Object {
 public:
  // Naming
  int GoodFuncion1();
  int badFuncion1();
  int Bad_Funcion2();

  // const reference
  int GoodFuncion2(const Object& o1);
  int BadFuncion3(Object& o1);

  // output arguments order
  int GoodFuncion3(const Object& o1, int i, int* j);
  int BadFuncion4(const Object& o1, int i, int* j, int k);
  int BadFuncion4(int* j, const Object& k);
};

int Main() {
  return 0;
}
