export type Token = {
  access_token: string;
  token_type: string;
};

export type UserPrivate = {
  id: number;
  username: string;
  email: string;
  image_file: string | null;
  image_path: string;
};
