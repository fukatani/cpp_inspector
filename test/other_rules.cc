int Main() {

  // C style cast is prohibited.
  int good = static_cast<int>(5);
  int bad_int = (int)5;
  float bad_float = (float)5;

  // sizeof(int) is not recommended.
  int good_size = sizeof(int);
  int bad_size = sizeof(good);

  return 0;
}
