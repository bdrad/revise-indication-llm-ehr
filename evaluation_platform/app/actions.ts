"use server"

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

import { createClient } from '@/app/utils/supabase/server'

export async function signout() {
  const supabase = await createClient()
  const { error } = await supabase.auth.signOut()
  if (error) {
        redirect('/error')
 }
  redirect('/login')
}

export async function getSetNumber() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  const { data, error } = await supabase
  .from("users")
  .select("user_id, set_id")
  .eq("user_id", user?.id)
  return data?.[0].set_id
}

export async function submitData(
  comprehensiveness1: Number,
  comprehensiveness2: Number,
  comprehensiveness3: Number,
  comprehensiveness4: Number,
  factuality1: Number,
  factuality2: Number,
  factuality3: Number,
  factuality4: Number,
  conciseness1: Number,
  conciseness2: Number,
  conciseness3: Number,
  conciseness4: Number,
  comment1: String,
  comment2: String,
  comment3: String,  
  comment4: String,  
  selectedIndication: String,
  setNumber: number  
) {

  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()


  let { data, error } = await supabase
  .from("users")
  .select("user_id, set_id")
  .eq("user_id", user?.id)

  let user_id = data?.[0].user_id

  let { error: insertError } = await supabase
      .from('evaluations')
      .insert({
        user_id: user_id,
        set_id: setNumber,
        indication_1_comprehensiveness: comprehensiveness1,
        indication_2_comprehensiveness: comprehensiveness2,
        indication_3_comprehensiveness: comprehensiveness3,
        indication_4_comprehensiveness: comprehensiveness4,
        indication_1_factuality: factuality1,
        indication_2_factuality: factuality2,
        indication_3_factuality: factuality3,
        indication_4_factuality: factuality4,
        indication_1_conciseness: conciseness1,
        indication_2_conciseness: conciseness2,
        indication_3_conciseness: conciseness3,
        indication_4_conciseness: conciseness4,
        indication_1_comment: comment1,
        indication_2_comment: comment2,
        indication_3_comment: comment3,
        indication_4_comment: comment4,
        indication_preference: selectedIndication
      });

    if (insertError) {
      throw insertError;
    }

  await supabase
  .from('users')
  .update({ set_id: setNumber+1 })
  .match({ user_id: user_id })

}